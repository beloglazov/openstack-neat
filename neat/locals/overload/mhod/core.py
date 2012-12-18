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

""" This is the main module of the MHOD algorithm.
"""

from contracts import contract
from neat.contracts_extra import *

from collections import deque

import neat.locals.overload.mhod.multisize_estimation as estimation
import neat.locals.overload.mhod.bruteforce as bruteforce
from neat.locals.overload.mhod.l_2_states import ls

import logging
log = logging.getLogger(__name__)


@contract
def mhod_factory(time_step, migration_time, params):
    """ Creates the MHOD algorithm.

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param params: A dictionary containing the algorithm's parameters.
     :type params: dict(str: *)

    :return: A function implementing the MHOD algorithm.
     :rtype: function
    """
    def mhod_wrapper(utilization, state=None):
        if not state:
            state = init_state(params['history_size'],
                               params['window_sizes'],
                               len(params['state_config']) + 1)
        return mhod(params['state_config'],
                    params['otf'],
                    params['window_sizes'],
                    params['bruteforce_step'],
                    params['learning_steps'],
                    time_step,
                    migration_time,
                    utilization,
                    state)
    return mhod_wrapper


@contract
def init_state(history_size, window_sizes, number_of_states):
    """ Initialize the state dictionary of the MHOD algorithm.

    :param history_size: The number of last system states to store.
     :type history_size: int,>0

    :param window_sizes: The required window sizes.
     :type window_sizes: list(int)

    :param number_of_states: The number of states.
     :type number_of_states: int,>0

    :return: The initialization state dictionary.
     :rtype: dict(str: *)
    """
    return {
        'previous_state': 0,
        'state_history': deque([], history_size),
        'request_windows': estimation.init_request_windows(
            number_of_states, max(window_sizes)),
        'estimate_windows': estimation.init_deque_structure(
            window_sizes, number_of_states),
        'variances': estimation.init_variances(
            window_sizes, number_of_states),
        'acceptable_variances': estimation.init_variances(
            window_sizes, number_of_states)}


@contract
def mhod(state_config, otf, window_sizes, bruteforce_step, learning_steps,
         time_step, migration_time, utilization, state):
    """ The MHOD algorithm returning whether the host is overloaded.

    :param state_config: The state configuration.
     :type state_config: list(float)

    :param otf: The OTF parameter.
     :type otf: float,>0

    :param window_sizes: A list of window sizes.
     :type window_sizes: list(int)

    :param bruteforce_step: The step of the bruteforce algorithm.
     :type bruteforce_step: float

    :param time_step: The length of the simulation time step in seconds.
     :type time_step: int,>=0

    :param migration_time: The VM migration time in time seconds.
     :type migration_time: float,>=0

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :param state: The state of the algorithm.
     :type state: dict

    :return: The updated state and decision of the algorithm.
     :rtype: tuple(bool, dict)
    """
    number_of_states = len(state_config) + 1
    previous_state = 0
    state['request_windows'] = estimation.init_request_windows(
        number_of_states, max(window_sizes))
    state['estimate_windows'] = estimation.init_deque_structure(
        window_sizes, number_of_states)
    state['variances'] = estimation.init_variances(
        window_sizes, number_of_states)
    state['acceptable_variances'] = estimation.init_variances(
        window_sizes, number_of_states)

    n = len(utilization)
    for i, current_state in enumerate(utilization_to_states(state_config, utilization)):
        if i == n - 1:
            selected_windows = estimation.select_window(
                state['variances'],
                state['acceptable_variances'],
                window_sizes)
            p = estimation.select_best_estimates(
                state['estimate_windows'],
                selected_windows)
            # These two are saved for testing purposes
            state['selected_windows'] = selected_windows
            state['p'] = p

        state['request_windows'] = estimation.update_request_windows(
            state['request_windows'],
            previous_state,
            current_state)
        state['estimate_windows'] = estimation.update_estimate_windows(
            state['estimate_windows'],
            state['request_windows'],
            previous_state)
        state['variances'] = estimation.update_variances(
            state['variances'],
            state['estimate_windows'],
            previous_state)
        state['acceptable_variances'] = estimation.update_acceptable_variances(
            state['acceptable_variances'],
            state['estimate_windows'],
            previous_state)
        previous_state = current_state

    state_vector = build_state_vector(state_config, utilization)
    current_state = get_current_state(state_vector)
    state['state_history'].append(current_state)
    state['previous_state'] = current_state

    if log.isEnabledFor(logging.DEBUG):
        log.debug('MHOD utilization:' + str(utilization))
        log.debug('MHOD state_history:' + str(state['state_history']))

    if len(utilization) >= learning_steps:
        #state_history = utilization_to_states(state_config, utilization)
        time_in_states = len(state['state_history'])
        time_in_state_n = get_time_in_state_n(state_config, state['state_history'])
        # These two are saved for testing purposes
        state['time_in_states'] = time_in_states
        state['time_in_state_n'] = time_in_state_n

        if log.isEnabledFor(logging.DEBUG):
            log.debug('MHOD time_in_states:' + str(time_in_states))
            log.debug('MHOD time_in_state_n:' + str(time_in_state_n))
            log.debug('MHOD p:' + str(p))
            log.debug('MHOD current_state:' + str(current_state))
            log.debug('MHOD p[current_state]:' + str(p[current_state]))

        tmp = set(p[current_state])
        if len(tmp) != 1 or 0 not in tmp:
            policy = bruteforce.optimize(
                bruteforce_step, 1.0, otf, (migration_time / time_step),
                ls, p, state_vector, time_in_states, time_in_state_n)
            # This is saved for testing purposes
            state['policy'] = policy
            if log.isEnabledFor(logging.DEBUG):
                log.debug('MHOD policy:' + str(policy))
            command = issue_command_deterministic(policy)
            if log.isEnabledFor(logging.DEBUG):
                log.debug('MHOD command:' + str(command))
            return command, state
    return False, state


@contract
def build_state_vector(state_config, utilization):
    """ Build the current state PMF corresponding to the utilization
        history and state config.

    :param state_config: The state configuration.
     :type state_config: list(float)

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The current state vector.
     :rtype: list(int)
    """
    state = utilization_to_state(state_config, utilization[-1])
    return [int(state == x) for x in range(len(state_config) + 1)]


@contract
def utilization_to_state(state_config, utilization):
    """ Transform a utilization value into the corresponding state.

    :param state_config: The state configuration.
     :type state_config: list(float)

    :param utilization: A utilization value.
     :type utilization: number,>=0

    :return: The state corresponding to the utilization value.
     :rtype: int
    """
    prev = -1
    for state, threshold in enumerate(state_config):
        if utilization >= prev and utilization < threshold:
            return state
        prev = state
    return prev + 1


@contract
def get_current_state(state_vector):
    """ Get the current state corresponding to the state probability vector.

    :param state_vector: The state PMF vector.
     :type state_vector: list(int)

    :return: The current state.
     :rtype: int,>=0
    """
    return state_vector.index(1)


@contract
def utilization_to_states(state_config, utilization):
    """ Get the state history corresponding to the utilization history.

    Adds the 0 state to the beginning to simulate the first transition.

    (map (partial utilization-to-state state-config) utilization))

    :param state_config: The state configuration.
     :type state_config: list(float)

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :return: The state history.
     :rtype: list(int)
    """
    return [utilization_to_state(state_config, x) for x in utilization]


@contract
def get_time_in_state_n(state_config, state_history):
    """ Get the number of time steps the system has been in the state N.

    :param state_config: The state configuration.
     :type state_config: list(float)

    :param state_history: The state history.
     :type state_history: deque

    :return: The total time the system has been in the state N.
     :rtype: int
    """
    return list(state_history).count(len(state_config))


@contract
def issue_command_deterministic(policy):
    """ Issue a migration command according to the policy PMF p.

    :param policy: A policy PMF.
     :type policy: list(number)

    :return: A migration command.
     :rtype: bool
    """
    return len(policy) == 0
