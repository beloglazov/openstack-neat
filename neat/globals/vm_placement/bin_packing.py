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
    # recalculate the available CPU capacity according to the threshold
    return lambda hosts_cpu, hosts_ram, vms_cpu, vms_ram, state=None: \
        (best_fit_decreasing(params['cpu_threshold'],
                             hosts_cpu, hosts_ram, vms_cpu, vms_ram), {})


@contract
def best_fit_decreasing(hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
                        vms_cpu, vms_ram):
    """ The Best Fit Decreasing (BFD) heuristic for placing VMs on hosts.

    :param hosts_cpu: A map of host names and their available CPU frequency in MHz.
     :type hosts_cpu: dict(str: int)

    :param hosts_ram: A map of host names and their available RAM capacity in MB.
     :type hosts_ram: dict(str: int)

    :param inactive_hosts_cpu: A map of inactive hosts and their available CPU frequency in MHz.
     :type inactive_hosts_cpu: dict(str: int)

    :param inactive_hosts_ram: A map of inactive hosts and their available RAM capacity in MB.
     :type inactive_hosts_ram: dict(str: int)

    :param vms_cpu: A map of VM UUID and their CPU utilization in MHz.
     :type vms_cpu: dict(str: int)

    :param vms_ram: A map of VM UUID and their RAM usage in MB.
     :type vms_ram: dict(str: int)

    :return: A map of VM UUIDs to host names, or an empty dict if cannot be solved.
     :rtype: dict(str: str)
    """
    vms = sorted(((v, vms_ram[k], k) for k, v in vms_cpu.items()), reverse=True)
    hosts = sorted(((v, hosts_ram[k], k) for k, v in hosts_cpu.items()))
    inactive_hosts = sorted(((v, inactive_hosts_ram[k], k) for k, v
                             in inactive_hosts_cpu.items()))
    print vms
    print hosts
    mapping = {}
    for vm_cpu, vm_ram, vm_uuid in vms:
        mapped = False
        while not mapped or inactive_hosts:
            for _, _, host in hosts:
                print "-----"
                print vm_uuid
                print vm_cpu
                print vms_ram[vm_uuid]
                print host
                print hosts_cpu[host]
                print hosts_ram[host]
                if hosts_cpu[host] >= vm_cpu and \
                  hosts_ram[host] >= vm_ram:
                    print "mapped " + vm_uuid + " to " + host
                    mapping[vm_uuid] = host
                    hosts_cpu[host] -= vm_cpu
                    hosts_ram[host] -= vm_ram
                    mapped = True
                    break
            else:
                if inactive_hosts:
                    activated_host = inactive_hosts.pop(0)
                    hosts.append(activated_host)
                    hosts = sorted(hosts)
                    print " +++ added a new host: " + str(activated_host)
                    print "hosts: " + str(hosts)

    print mapping
    if len(vms) == len(mapping):
        return mapping
    return {}
