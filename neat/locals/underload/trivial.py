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

""" Trivial underload detection algorithms.
"""

from contracts import contract
from neat.contracts_extra import *

import logging
log = logging.getLogger(__name__)


@contract
def always_underloaded_factory(time_step, migration_time, params):
    """ Creates an algorithm that always considers the host underloaded.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the algorithm.
     :rtype: function
    """
    return lambda utilization, state=None: (True, {})


@contract
def threshold_factory(time_step, migration_time, params):
    """ Creates the threshold underload detection algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the OTF algorithm.
     :rtype: function
    """
    return lambda utilization, state=None: (threshold(params['threshold'],
                                                      utilization),
                                            {})

@contract
def last_n_average_threshold_factory(time_step, migration_time, params):
    """ Creates the averaging threshold underload detection algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the averaging underload detection.
     :rtype: function
    """
    return lambda utilization, state=None: (
        last_n_average_threshold(params['threshold'],
                                 params['n'],
                                 utilization),
        {})


@contract
def threshold(threshold, utilization):
    """ Static threshold-based underload detection algorithm.

    The algorithm returns True, if the last value of the host's
    CPU utilization is lower than the specified threshold.

    :param threshold: The static underload CPU utilization threshold.
     :type threshold: float,>=0,<=1

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: A decision of whether the host is underloaded.
     :rtype: bool
    """
    if utilization:
        return utilization[-1] <= threshold
    return False


@contract
def last_n_average_threshold(threshold, n, utilization):
    """ Averaging static threshold-based underload detection algorithm.

    The algorithm returns True, if the average of the last n values of
    the host's CPU utilization is lower than the specified threshold.

    :param threshold: The static underload CPU utilization threshold.
     :type threshold: float,>=0,<=1

    :param n: The number of last values to average.
     :type n: int,>0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: A decision of whether the host is underloaded.
     :rtype: bool
    """
    if utilization:
        utilization = utilization[-n:]
        return sum(utilization) / len(utilization) <= threshold
    return False
