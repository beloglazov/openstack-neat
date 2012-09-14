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

import neat.local.overload.mhod.multisize_estimation as estimation
import neat.local.overload.mhod.bruteforce as bruteforce
from neat.local.overload.mhod.l_2_states import ls


@contract
def init_state(window_sizes, number_of_states):
    """ Initialize the state dictionary of the MHOD algorithm.

    :param window_sizes: The required window sizes.
     :type window_sizes: list(int)

    :param number_of_states: The number of states.
     :type number_of_states: int,>0

    :return: The initialization state dictionary.
     :rtype: dict(str: *)
    """
    state = {}
    state['previous_state'] = 0
    state['request_windows'] = estimation.init_request_windows(number_of_states)
    state['estimate_windows'] = estimation.init_deque_structure(window_sizes, number_of_states)
    state['variances'] = estimation.init_variances(window_sizes, number_of_states)
    state['acceptable_variances'] = estimation.init_variances(window_sizes, number_of_states)
    return state


@contract
def execute(state_config, otf, window_sizes, bruteforce_step,
            time_step, migration_time, utilization, state):
    """ The MHOD algorithm returning a decision of whether the host is overloaded.

    :param state_config: The state configuration.
     :type state_config: list(float)

    :param otf: The OTF parameter.
     :type otf: int,>0

    :param window_sizes: A list of window sizes.
     :type window_sizes: list(int)

    :param bruteforce_step: The step of the bruteforce algorithm.
     :type bruteforce_step: float

    :param time_step: The lenght of a time frame in seconds.
     :type time_step: int

    :param migration_time: The VM migration time in seconds.
     :type migration_time: int

    :param utilization: The history of the host's CPU utilization.
     :type utilization: list(float)

    :param state: The state of the algorithm.
     :type state: dict

    :return: The updated state and decision of the algorithm.
     :rtype: tuple(dict, bool)
    """
    total_time = len(utilization)
    max_window_size = max(window_sizes)
    state_vector = build_state_vector(state_config, utilization)
    state = current_state(state_vector)
    selected_windows = estimation.select_window(state['variances'],
                                                state['acceptable_variances'],
                                                window_sizes)
    p = estimation.select_best_estimates(state['estimate_windows'],
                                         selected_windows)

    state['request_windows'] = estimation.update_request_windows(state['request_windows'],
                                                                 max_window_size,
                                                                 state['previous_state'],
                                                                 state)
    state['estimate_windows'] = estimation.update_estimate_windows(state['estimate_windows'],
                                                                   state['request_windows'],
                                                                   state['previous_state'])
    state['variances'] = estimation.update_variances(state['variances'],
                                                     state['estimate_windows'],
                                                     state['previous_state'])
    state['acceptable_variances'] = estimation.update_acceptable_variances(state['acceptable_variances'],
                                                                           state['estimate_windows'],
                                                                           state['previous_state'])
    state['previous_state'] = state

    if len(utilization) >= 30:
        state_history = utilization_to_states(state_config, utilization)
        time_in_states = total_time
        time_in_state_n = get_time_in_state_n(state_config, state_history)
        tmp = set(p[state])
        if len(tmp) != 1 or tmp[0] != 0:
            policy = bruteforce.optimize(step, 1.0, otf, (migration_time / time_step), ls,
                                         p, state_vector, time_in_states, time_in_state_n)
            return issue_command_deterministic(policy)
    return false


@contract
def build_state_vector(state_config, utilization):
    """ Build the current state PMF corresponding to the utilization history and state config.

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
def current_state(state_vector):
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
     :type state_history: list(int)

    :return: The total time the system has been in the state N.
     :rtype: int
    """
    return state_history.count(len(state_config))


@contract
def issue_command_deterministic(policy):
    """ Issue a migration command according to the policy PMF p.

    :param policy: A policy PMF.
     :type policy: list(number)

    :return: A migration command.
     :rtype: bool
    """
    return len(policy) == 0
