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

""" OTF threshold based algorithms.
"""

from contracts import contract
from neat.contracts_extra import *


@contract
def otf_factory(time_step, migration_time, params):
    """ Creates the OTF algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the OTF algorithm.
     :rtype: function
    """
    return lambda utilization, state=None: (otf(params['threshold'],
                                                utilization),
                                            {})


@contract
def otf_limit_factory(time_step, migration_time, params):
    """ Creates the OTF algorithm with limiting.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the OTF algorithm with limiting.
     :rtype: function
    """
    return lambda utilization, state=None: (otf_limit(params['threshold'],
                                                      params['limit'],
                                                      utilization),
                                            {})


@contract
def otf_migration_time_factory(time_step, migration_time, params):
    """ Creates the OTF algorithm considering the migration time.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the OTF algorithm.
     :rtype: function
    """
    migration_time_normalized = float(migration_time) / time_step
    return lambda utilization, state=None: (otf_migration_time(params['threshold'],
                                                               migration_time_normalized,
                                                               utilization),
                                            {})


@contract
def otf_limit_migration_time_factory(time_step, migration_time, params):
    """ Creates the OTF algorithm with limiting and migration time.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: int,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the OTF algorithm.
     :rtype: function
    """
    migration_time_normalized = float(migration_time) / time_step
    return lambda utilization, state=None: (otf_limit_migration_time(params['threshold'],
                                                                     params['limit'],
                                                                     migration_time_normalized,
                                                                     utilization),
                                            {})


@contract
def otf(threshold, utilization):
    """ The OTF threshold algorithm.

    :param threshold: The threshold on the OTF value.
     :type threshold: float,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm.
     :rtype: bool
    """
    return float(overloading_steps(utilization)) / len(utilization) > threshold


@contract
def otf_limit(threshold, limit, utilization):
    """ The OTF threshold algorithm with limiting the minimum utilization values.

    :param threshold: The threshold on the OTF value.
     :type threshold: float,>=0

    :param limit: The minimum number of values in the utilization history.
     :type limit: int,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm.
     :rtype: bool
    """
    cnt = len(utilization)
    if cnt < limit:
        return False
    return float(overloading_steps(utilization)) / cnt > threshold


@contract
def otf_migration_time(threshold, migration_time, utilization):
    """ The OTF threshold algorithm considering the migration time.

    :param threshold: The threshold on the OTF value.
     :type threshold: float,>=0

    :param migration_time: The VM migration time in time steps.
     :type migration_time: number,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm.
     :rtype: bool
    """
    return (migration_time + float(overloading_steps(utilization))) / \
        (migration_time + len(utilization)) > threshold


@contract
def otf_limit_migration_time(threshold, limit, migration_time, utilization):
    """ The OTF threshold algorithm with limiting and migration time.

    :param threshold: The threshold on the OTF value.
     :type threshold: float,>=0

    :param limit: The minimum number of values in the utilization history.
     :type limit: int,>=0

    :param migration_time: The VM migration time in time steps.
     :type migration_time: number,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The decision of the algorithm.
     :rtype: bool
    """
    cnt = len(utilization)
    if cnt < limit:
        return False
    return (migration_time + float(overloading_steps(utilization))) / \
        (migration_time + cnt) > threshold


@contract
def overloading_steps(utilization):
    """ Get the number of overloading steps (utilization >= 100%).

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The number of overloading steps.
     :rtype: int
    """
    return len([1 for x in utilization if x >= 1])
