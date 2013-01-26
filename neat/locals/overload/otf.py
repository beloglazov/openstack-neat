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

import logging
log = logging.getLogger(__name__)


@contract
def otf_factory(time_step, migration_time, params):
    """ Creates the OTF algorithm with limiting and migration time.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the OTF algorithm.
     :rtype: function
    """
    migration_time_normalized = float(migration_time) / time_step
    def otf_wrapper(utilization, state=None):
        if state is None or state == {}:
            state = {'overload': 0, 
                     'total': 0}
        return otf(params['otf'],
                   params['threshold'],
                   params['limit'],
                   migration_time_normalized,
                   utilization,
                   state)
    
    return otf_wrapper
        

@contract
def otf(otf, threshold, limit, migration_time, utilization, state):
    """ The OTF threshold algorithm with limiting and migration time.

    :param otf: The threshold on the OTF value.
     :type otf: float,>=0

    :param threshold: The utilization overload threshold.
     :type threshold: float,>=0

    :param limit: The minimum number of values in the utilization history.
     :type limit: int,>=0

    :param migration_time: The VM migration time in time steps.
     :type migration_time: float,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :param state: The state dictionary.
     :type state: dict(str: *)

    :return: The decision of the algorithm and updated state.
     :rtype: tuple(bool, dict(*: *))
    """
    state['total'] += 1
    overload = (utilization[-1] >= threshold)
    if overload:
        state['overload'] += 1

    if log.isEnabledFor(logging.DEBUG):
        log.debug('OTF overload:' + str(overload))
        log.debug('OTF overload steps:' + str(state['overload']))
        log.debug('OTF total steps:' + str(state['total']))
        log.debug('OTF:' + str(float(state['overload']) / state['total']))
        log.debug('OTF migration time:' + str(migration_time))
        log.debug('OTF + migration time:' + 
                  str((migration_time + state['overload']) / \
                          (migration_time + state['total'])))
        log.debug('OTF decision:' + 
                  str(overload and (migration_time + state['overload']) / \
                          (migration_time + state['total']) >= otf))

    if not overload or len(utilization) < limit:
        decision = False
    else:
        decision = (migration_time + state['overload']) / \
            (migration_time + state['total']) >= otf

    return (decision, state)
