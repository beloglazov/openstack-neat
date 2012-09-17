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

# @contract
# def threshold_factory(time_step, migration_time, params):
#     """ Creates the threshold underload detection algorithm.

#     :param time_step: The length of the simulation time step in seconds.
#      :type time_step: int,>=0

#     :param migration_time: The VM migration time in time seconds.
#      :type migration_time: int,>=0

#     :param params: A dictionary containing the algorithm's parameters.
#      :type params: dict(str: *)

#     :return: A function implementing the OTF algorithm.
#      :rtype: function
#     """
#     return lambda utilization, state=None: (threshold(params['threshold'],
#                                                       utilization),
#                                             {})


@contract
def minimum_utilization(vms):
    """ Selects the VM with the minimum CPU utilization.

    :param vms: A map of VM UUID and their CPU utilization histories.
     :type vms: dict(str: list)

    :return: A VM to migrate from the host.
     :rtype: str
    """
    last_utilization = [x[-1] for x in vms.values()]
    min_index, min_value = min(enumerate(last_utilization), key=operator.itemgetter(1))
    return vms.keys()[min_index]


@contract
def random(vms):
    """ Selects a random VM.

    :param vms: A map of VM UUID and their CPU utilization histories.
     :type vms: dict(str: list)

    :return: A VM to migrate from the host.
     :rtype: str
    """
    return choice(vms.keys())
