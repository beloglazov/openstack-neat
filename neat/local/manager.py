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

import neat.common as common
from neat.config import *
from neat.db_utils import *


@contract
def start():
    """ Start the local manager loop.

    :return: The final state.
     :rtype: dict(str: *)
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH], REQUIRED_FIELDS)
    return common.start(
        init_state,
        execute,
        config,
        config.get('local_manager_interval'))


@contract
def init_state(config):
    """ Initialize a dict for storing the state of the local manager.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dictionary containing the initial state of the data collector.
     :rtype: dict
    """
    vir_connection = libvirt.openReadOnly(None)
    if vir_connection is None:
        print 'Failed to open connection to the hypervisor'
        sys.exit(1)
    return {'previous_time': 0,
            'vir_connect': vir_connection,
            'db': init_db(config.get('sql_connection')),
            'physical_cpu_mhz_total': common.physical_cpu_mhz_total(vir_connection)}


@contract
def execute(config, state):
    """ Execute a local manager iteration.

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

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param state: A state dictionary.
     :type state: dict(str: *)

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    path = common.build_local_vm_path(config.get('local_data_directory'))
    vm_data = get_local_data(path)


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
