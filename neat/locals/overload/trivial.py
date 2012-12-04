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

""" Trivial overload detection algorithms.
"""

from contracts import contract
from neat.contracts_extra import *

import logging
log = logging.getLogger(__name__)


@contract
def never_overloaded_factory(time_step, migration_time, params):
    """ Creates an algorithm that never considers the host overloaded.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the algorithm.
     :rtype: function
    """
    return lambda utilization, state=None: (False, {})


@contract
def threshold_factory(time_step, migration_time, params):
    """ Creates the static CPU utilization threshold algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the static threshold algorithm.
     :rtype: function
    """
    return lambda utilization, state=None: (threshold(params['threshold'],
                                                      utilization),
                                            {})


@contract
def last_n_average_threshold_factory(time_step, migration_time, params):
    """ Creates the averaging CPU utilization threshold algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the averaging threshold algorithm.
     :rtype: function
    """
    return lambda utilization, state=None: (
        last_n_average_threshold(params['threshold'],
                                 params['n'],
                                 utilization),
        {})


@contract
def threshold(threshold, utilization):
    """ The static CPU utilization threshold algorithm.

    :param threshold: The threshold on the CPU utilization.
     :type threshold: float,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm.
     :rtype: bool
    """
    if utilization:
        return utilization[-1] > threshold
    return False


@contract
def last_n_average_threshold(threshold, n, utilization):
    """ The averaging CPU utilization threshold algorithm.

    :param threshold: The threshold on the CPU utilization.
     :type threshold: float,>=0

    :param n: The number of last CPU utilization values to average.
     :type n: int,>0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm.
     :rtype: bool
    """
    if utilization:
        utilization = utilization[-n:]
        return sum(utilization) / len(utilization) > threshold
    return False
