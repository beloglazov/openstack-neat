# Copyright 2012 Anton Beloglazov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" The main local manager module.

The local manager component is deployed on every compute host and is
invoked periodically to determine when it necessary to reallocate VM
instances from the host. First of all, it reads from the local storage
the historical data on the resource usage by VMs stored by the data
collector. Then, the local manager invokes the specified in the
configuration underload detection algorithm to determine whether the
host is underloaded. If the host is underloaded, the local manager
sends a request to the global manager's REST API to migrate all the
VMs from the host and switch the host to the sleep mode.

If the host is not underloaded, the local manager proceeds to invoking
the specified in the configuration overload detection algorithm. If
the host is overloaded, the local manager invokes the configured VM
selection algorithm to select the VMs to migrate from the host. Once
the VMs to migrate from the host are selected, the local manager sends
a request to the global manager's REST API to migrate the selected VMs
from the host.

Similarly to the global manager, the local manager can be configured
to use specific underload detection, overload detection, and VM
selection algorithm using the configuration file discussed further in
the paper.

Underload detection is done by a specified in the configuration
underload detection algorithm (algorithm_underload_detection). The
algorithm has a pre-defined interface, which allows substituting
different implementations of the algorithm. The configured algorithm
is invoked by the local manager and accepts historical data on the
resource usage by VMs running on the host as an input. An underload
detection algorithm returns a decision of whether the host is
underloaded.

Overload detection is done by a specified in the configuration
overload detection algorithm (algorithm_overload_detection). Similarly
to underload detection, all overload detection algorithms implement a
pre-defined interface to enable configuration-driven substitution of
difference implementations. The configured algorithm is invoked by the
local manager and accepts historical data on the resource usage by VMs
running on the host as an input. An overload detection algorithm
returns a decision of whether the host is overloaded.

If a host is overloaded, it is necessary to select VMs to migrate from
the host to avoid performance degradation. This is done by a specified
in the configuration VM selection algorithm (algorithm_vm_selection).
Similarly to underload and overload detection algorithms, different VM
selection algorithm can by plugged in according to the configuration.
A VM selection algorithm accepts historical data on the resource usage
by VMs running on the host and returns a set of VMs to migrate from
the host.

The local manager will be implemented as a Linux daemon running in the
background and every local_manager_interval seconds checking whether
some VMs should be migrated from the host. Every time interval, the
local manager performs the following steps:

1. Read the data on resource usage by the VMs running on the host from
   the <local_data_directory>/vm directory.

2. Call the function specified in the algorithm_underload_detection
   configuration option and pass the data on the resource usage by the
   VMs, as well as the frequency of the CPU as arguments.

3. If the host is underloaded, send a request to the REST API of the
   global manager and pass a list of the UUIDs of all the VMs
   currently running on the host in the vm_uuids parameter, as well as
   the reason for migration as being 0.

4. If the host is not underloaded, call the function specified in the
   algorithm_overload_detection configuration option and pass the data
   on the resource usage by the VMs, as well as the frequency of the
   host's CPU as arguments.

5. If the host is overloaded, call the function specified in the
   algorithm_vm_selection configuration option and pass the data on
   the resource usage by the VMs, as well as the frequency of the
   host's CPU as arguments

6. If the host is overloaded, send a request to the REST API of the
   global manager and pass a list of the UUIDs of the VMs selected by
   the VM selection algorithm in the vm_uuids parameter, as well as
   the reason for migration as being 1.

7. Schedule the next execution after local_manager_interval seconds.
"""

from contracts import contract
from neat.contracts_extra import *

import json
import numpy
import itertools

import neat.common as common
from neat.config import *
from neat.db_utils import *

import logging
log = logging.getLogger(__name__)


@contract
def start():
    """ Start the local manager loop.

    :return: The final state.
     :rtype: dict(str: *)
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                      REQUIRED_FIELDS)

    common.init_logging(
        config['log_directory'],
        'local-manager.log',
        int(config['log_level']))

    interval = config['local_manager_interval']
    log.info('Starting the local manager, ' +
             'iterations every %s seconds', interval)
    return common.start(
        init_state,
        execute,
        config,
        int(interval))


@contract
def init_state(config):
    """ Initialize a dict for storing the state of the local manager.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dictionary containing the initial state of the local manager.
     :rtype: dict
    """
    vir_connection = libvirt.openReadOnly(None)
    if vir_connection is None:
        message = 'Failed to open a connection to the hypervisor'
        log.critical(message)
        raise OSError(message)

    physical_cpu_mhz_total = common.physical_cpu_mhz_total(vir_connection)
    return {'previous_time': 0.,
            'vir_connection': vir_connection,
            'db': init_db(config['sql_connection']),
            'physical_cpu_mhz_total': physical_cpu_mhz_total}


@contract
def execute(config, state):
    """ Execute an iteration of the local manager.

1. Read the data on resource usage by the VMs running on the host from
   the <local_data_directory>/vm directory.

2. Call the function specified in the algorithm_underload_detection
   configuration option and pass the data on the resource usage by the
   VMs, as well as the frequency of the CPU as arguments.

3. If the host is underloaded, send a request to the REST API of the
   global manager and pass a list of the UUIDs of all the VMs
   currently running on the host in the vm_uuids parameter, as well as
   the reason for migration as being 0.

4. If the host is not underloaded, call the function specified in the
   algorithm_overload_detection configuration option and pass the data
   on the resource usage by the VMs, as well as the frequency of the
   host's CPU as arguments.

5. If the host is overloaded, call the function specified in the
   algorithm_vm_selection configuration option and pass the data on
   the resource usage by the VMs, as well as the frequency of the
   host's CPU as arguments

6. If the host is overloaded, send a request to the REST API of the
   global manager and pass a list of the UUIDs of the VMs selected by
   the VM selection algorithm in the vm_uuids parameter, as well as
   the reason for migration as being 1.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param state: A state dictionary.
     :type state: dict(str: *)

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    path = common.build_local_vm_path(config['local_data_directory'])
    vm_cpu_mhz = get_local_data(path)
    vm_ram = get_ram(state['vir_connection'], vm_cpu_mhz.keys())
    vm_cpu_mhz = cleanup_vm_data(vm_cpu_mhz, vm_ram.keys())

    if not vm_cpu_mhz:
        return

    physical_cpu_mhz_total = int(config['physical_cpu_mhz_total'])
    host_cpu_utilization = vm_mhz_to_percentage(
        vm_cpu_mhz, physical_cpu_mhz_total)
    time_step = int(config['data_collector_interval'])
    migration_time = calculate_migration_time(
        vm_ram, float(config['network_migration_bandwidth']))

    if 'underload_detection' not in state:
        underload_detection_params = json.loads(
            config['algorithm_underload_detection_params'])
        underload_detection_state = None
        underload_detection = \
            config['algorithm_underload_detection_factory'](
                time_step,
                migration_time,
                underload_detection_params)
        state['underload_detection'] = underload_detection

        overload_detection_params = json.loads(
            config['algorithm_overload_detection_params'])
        overload_detection_state = None
        overload_detection = \
            config['algorithm_overload_detection_factory'](
                time_step,
                migration_time,
                overload_detection_params)
        state['overload_detection'] = overload_detection

        vm_selection_params = json.loads(
            config['algorithm_vm_selection_params'])
        vm_selection_state = None
        vm_selection = \
            config['algorithm_vm_selection_factory'](
                time_step,
                migration_time,
                vm_selection_params)
        state['vm_selection'] = vm_selection
    else:
        underload_detection = state['underload_detection']
        underload_detection_state = state['underload_detection_state']
        overload_detection = state['overload_detection']
        overload_detection_state = state['overload_detection_state']
        vm_selection = state['vm_selection']
        vm_selection_state = state['vm_selection_state']

    underload, underload_detection_state = underload_detection(
        host_cpu_utilization, underload_detection_state)
    state['underload_detection_state'] = underload_detection_state

    if underload:
        log.info('Underload detected')
        # Send a request to the global manager with the host name
        pass
    else:
        overload, overload_detection_state = overload_detection(
            host_cpu_utilization, overload_detection_state)
        state['overload_detection_state'] = overload_detection_state
        if overload:
            log.info('Overload detected')
            vms = vm_selection(
                host_cpu_utilization, vm_ram, vm_selection_state)
            log.info('Selected VMs to migrate: %s', str(vms))
            # send a request to the global manager
            # with the selected VMs to migrate

    return state


@contract
def get_local_data(path):
    """ Read the data about VMs from the local storage.

    :param path: A path to read VM UUIDs from.
     :type path: str

    :return: A map of VM UUIDs onto the corresponing CPU MHz values.
     :rtype: dict(str : list(int))
    """
    result = {}
    for uuid in os.listdir(path):
        with open(os.path.join(path, uuid), 'r') as f:
            result[uuid] = [int(x) for x in f.read().strip().splitlines()]
    return result


@contract
def cleanup_vm_data(vm_data, uuids):
    """ Remove records for the VMs that are not in the list of UUIDs.

    :param vm_data: A map of VM UUIDs to some data.
     :type vm_data: dict(str: *)

    :param uuids: A list of VM UUIDs.
     :type uuids: list(str)

    :return: The cleaned up map of VM UUIDs to data.
     :rtype: dict(str: *)
    """
    for uuid, _ in vm_data.items():
        if uuid not in uuids:
            del vm_data[uuid]
    return vm_data


@contract
def get_ram(vir_connection, vms):
    """ Get the maximum RAM for a set of VM UUIDs.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :param vms: A list of VM UUIDs.
     :type vms: list(str)

    :return: The maximum RAM for the VM UUIDs.
     :rtype: dict(str : int)
    """
    vms_ram = {}
    for uuid in vms:
        ram = get_max_ram(vir_connection, uuid)
        if ram:
            vms_ram[uuid] = ram

    return vms_ram


@contract
def get_max_ram(vir_connection, uuid):
    """ Get the max RAM allocated to a VM UUID using libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :param uuid: The UUID of a VM.
     :type uuid: str[36]

    :return: The maximum RAM of the VM in MB.
     :rtype: int|None
    """
    domain = vir_connection.lookupByUUIDString(uuid)
    if domain:
        return domain.maxMemory() / 1024
    return None


@contract
def vm_mhz_to_percentage(vms, physical_cpu_mhz):
    """ Convert VM CPU utilization to the host's CPU utilization.

    :param vms: A map from VM UUIDs to their CPU utilization in MHz.
     :type vms: dict(str: list(int))

    :param physical_cpu_mhz: The total frequency of the physical CPU in MHz.
     :type physical_cpu_mhz: int

    :return: The history of the host's CPU utilization in percentages.
     :rtype: list(float)
    """
    data = itertools.izip_longest(*vms.values(), fillvalue=0)
    return [float(sum(x)) / physical_cpu_mhz for x in data]


@contract
def calculate_migration_time(vms, bandwidth):
    """ Calculate the mean migration time from VM RAM usage data.

    :param vms: A map of VM UUIDs to the corresponding maximum RAM in MB.
     :type vms: dict(str: int)

    :param bandwidth: The network bandwidth in MB/s.
     :type bandwidth: float,>0

    :return: The mean VM migration time in seconds.
     :rtype: float
    """
    return float(numpy.mean(vms.values()) / bandwidth)
