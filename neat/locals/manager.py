
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

import itertools
import requests
from hashlib import sha1
import time

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
    if log.isEnabledFor(logging.INFO):
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

    physical_cpu_mhz_total = int(
        common.physical_cpu_mhz_total(vir_connection) * 
        float(config['host_cpu_usable_by_vms']))
    return {'previous_time': 0.,
            'vir_connection': vir_connection,
            'db': init_db(config['sql_connection']),
            'physical_cpu_mhz_total': physical_cpu_mhz_total,
            'hostname': vir_connection.getHostname(),
            'hashed_username': sha1(config['os_admin_user']).hexdigest(),
            'hashed_password': sha1(config['os_admin_password']).hexdigest()}


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
        if log.isEnabledFor(logging.INFO):
            log.info('The host is idle')
        return state

    #TODO: update this with host CPU MHz
    host_cpu_utilization = vm_mhz_to_percentage(
        vm_cpu_mhz.values(), 
        state['physical_cpu_mhz_total'])
    time_step = int(config['data_collector_interval'])
    migration_time = common.calculate_migration_time(
        vm_ram, float(config['network_migration_bandwidth']))

    if 'underload_detection' not in state:
        underload_detection_params = common.parse_parameters(
            config['algorithm_underload_detection_parameters'])
        underload_detection_state = None
        underload_detection = common.call_function_by_name(
            config['algorithm_underload_detection_factory'],
            [time_step,
             migration_time,
             underload_detection_params])
        state['underload_detection'] = underload_detection
        state['underload_detection_state'] = {}

        overload_detection_params = common.parse_parameters(
            config['algorithm_overload_detection_parameters'])
        overload_detection_state = None
        overload_detection = common.call_function_by_name(
            config['algorithm_overload_detection_factory'],
            [time_step,
             migration_time,
             overload_detection_params])
        state['overload_detection'] = overload_detection
        state['overload_detection_state'] = {}

        vm_selection_params = common.parse_parameters(
            config['algorithm_vm_selection_parameters'])
        vm_selection_state = None
        vm_selection = common.call_function_by_name(
            config['algorithm_vm_selection_factory'],
            [time_step,
             migration_time,
             vm_selection_params])
        state['vm_selection'] = vm_selection
        state['vm_selection_state'] = {}
    else:
        underload_detection = state['underload_detection']
        overload_detection = state['overload_detection']
        vm_selection = state['vm_selection']

    underload, state['underload_detection_state'] = underload_detection(
        host_cpu_utilization, state['underload_detection_state'])

    if underload:
        if log.isEnabledFor(logging.INFO):
            log.info('Underload detected')
        try:
            r = requests.put('http://' + config['global_manager_host'] + \
                                 ':' + config['global_manager_port'], 
                             {'username': state['hashed_username'], 
                              'password': state['hashed_password'], 
                              'time': time.time(),
                              'reason': 0, 
                              'host': state['hostname']})
            if log.isEnabledFor(logging.INFO):
                log.info('Received response: [%s] %s', 
                         r.status_code, r.content)
        except requests.exceptions.ConnectionError:
            log.exception('Exception at underload request:')

    else:
        overload, state['overload_detection_state'] = overload_detection(
            host_cpu_utilization, state['overload_detection_state'])
        if overload:
            if log.isEnabledFor(logging.INFO):
                log.info('Overload detected')
            vm_uuids, state['vm_selection_state'] = vm_selection(
                host_cpu_utilization, vm_ram, state['vm_selection_state'])
            if log.isEnabledFor(logging.INFO):
                log.info('Selected VMs to migrate: %s', str(vm_uuids))
            try:
                r = requests.put('http://' + config['global_manager_host'] + \
                                     ':' + config['global_manager_port'], 
                                 {'username': state['hashed_username'], 
                                  'password': state['hashed_password'], 
                                  'time': time.time(),
                                  'reason': 1, 
                                  'vm_uuids': ','.join(vm_uuids)})
                if log.isEnabledFor(logging.INFO):
                    log.info('Received response: [%s] %s', 
                             r.status_code, r.content)
            except requests.exceptions.ConnectionError:
                log.exception('Exception at overload request:')
        else:
            if log.isEnabledFor(logging.INFO):
                log.info('No underload or overload detected')

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
    try: 
        domain = vir_connection.lookupByUUIDString(uuid)
        return domain.maxMemory() / 1024
    except libvirt.libvirtError:
        return None


@contract
def vm_mhz_to_percentage(vm_mhz_history, host_mhz_history, physical_cpu_mhz):
    """ Convert VM CPU utilization to the host's CPU utilization.

    :param vm_mhz_history: A list of CPU utilization histories of VMs in MHz.
     :type vm_mhz_history: list(list(int))

    :param host_mhz_history: A history if the CPU usage by the host in MHz.
     :type host_mhz_history: list(int)

    :param physical_cpu_mhz: The total frequency of the physical CPU in MHz.
     :type physical_cpu_mhz: int

    :return: The history of the host's CPU utilization in percentages.
     :rtype: list(float)
    """
    max_len = max(len(x) for x in vm_mhz_history)
    if len(host_mhz_history) > max_len:
        host_mhz_history = host_mhz_history[-max_len:]
    mhz_history = [[0] * (max_len - len(x)) + x
                   for x in vm_mhz_history + [host_mhz_history]]
    return [float(sum(x)) / physical_cpu_mhz for x in zip(*mhz_history)]
