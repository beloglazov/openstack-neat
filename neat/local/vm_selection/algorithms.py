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

""" VM selection algorithms.
"""

from contracts import contract
from neat.contracts_extra import *

from random import choice
import operator


@contract
def random_factory(time_step, migration_time, params):
    """ Creates the random VM selection algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the random VM selection algorithm.
     :rtype: function
    """
    return lambda vms_cpu, vms_ram, state=None: (random(vms_cpu), {})


@contract
def minimum_utilization_factory(time_step, migration_time, params):
    """ Creates the minimum utilization VM selection algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the minimum utilization VM selection algorithm.
     :rtype: function
    """
    return lambda vms_cpu, vms_ram, state=None: (minimum_utilization(vms_cpu), {})


@contract
def minimum_migration_time_factory(time_step, migration_time, params):
    """ Creates the minimum migration time VM selection algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the minimum migration time VM selection algorithm.
     :rtype: function
    """
    return lambda vms_cpu, vms_ram, state=None: (minimum_migration_time(vms_ram), {})


@contract
def minimum_migration_time(vms_ram):
    """ Selects the VM with the minimum RAM usage.

    :param vms_ram: A map of VM UUID and their RAM usage data.
     :type vms_ram: dict(str: number)

    :return: A VM to migrate from the host.
     :rtype: str
    """
    min_index, min_value = min(enumerate(vms_ram.values()), key=operator.itemgetter(1))
    return vms_ram.keys()[min_index]


@contract
def minimum_utilization(vms_cpu):
    """ Selects the VM with the minimum CPU utilization.

    :param vms_cpu: A map of VM UUID and their CPU utilization histories.
     :type vms_cpu: dict(str: list)

    :return: A VM to migrate from the host.
     :rtype: str
    """
    last_utilization = [x[-1] for x in vms_cpu.values()]
    min_index, min_value = min(enumerate(last_utilization), key=operator.itemgetter(1))
    return vms_cpu.keys()[min_index]


@contract
def random(vms_cpu):
    """ Selects a random VM.

    :param vms_cpu: A map of VM UUID and their CPU utilization histories.
     :type vms_cpu: dict(str: list)

    :return: A VM to migrate from the host.
     :rtype: str
    """
    return choice(vms_cpu.keys())
