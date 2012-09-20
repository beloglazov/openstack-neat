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

""" Bin Packing based VM placement algorithms.
"""

from contracts import contract
from neat.contracts_extra import *


@contract
def best_fit_decreasing_factory(time_step, migration_time, params):
    """ Creates the Best Fit Decreasing (BFD) heuristic for placing VMs on hosts.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the BFD algorithm.
     :rtype: function
    """
    return lambda hosts_cpu, hosts_ram, vms_cpu, vms_ram, state=None: \
        (best_fit_decreasing(hosts_cpu, hosts_ram, vms_cpu, vms_ram), {})


@contract
def best_fit_decreasing(cpu_threshold, hosts_cpu, hosts_ram, vms_cpu, vms_ram):
    """ The Best Fit Decreasing (BFD) heuristic for placing VMs on hosts.

    :param cpu_threshold: The host maximum CPU utilization for placing VMs.
     :type cpu_threshold: float

    :param hosts_cpu: A map of host names and their available CPU frequency in MHz.
     :type hosts_cpu: dict(str: int)

    :param hosts_ram: A map of host names and their available RAM capacity in MB.
     :type hosts_ram: dict(str: number)

    :param vms_cpu: A map of VM UUID and their CPU utilization in MHz.
     :type vms_cpu: dict(str: float)

    :param vms_ram: A map of VM UUID and their RAM usage in MB.
     :type vms_ram: dict(str: number)

    :return: A map of VM UUIDs to host names.
     :rtype: dict(str: str)
    """
    vms = sorted(((v, k) for k, v in vms_cpu.items()), reverse=True)
    hosts = sorted(((v, k) for k, v in hosts_cpu.items()))
    mapping = {}
    for (vm_cpu, vm_uuid), host in zip(vms, hosts):
        if host[0] * cpu_threshold >= vm_cpu and \
           hosts_ram[host[1]] >= vms_ram[vm_uuid]:
            mapping[vm_uuid] = host[1]
            host[0] -= vm_cpu
            hosts_ram[host[1]] -= vms_ram[vm_uuid]

    if len(vms) == len(mapping):
        return mapping
    return {}
