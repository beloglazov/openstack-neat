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
    state['request_windows'] = init_request_windows(number_of_states)
    state['estimate_windows'] = init_deque_structure(window_sizes, number_of_states)
    state['variances'] = init_variances(window_sizes, number_of_states)
    state['acceptable_variances'] = init_variances(window_sizes, number_of_states)
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

(defn markov-multisize [step otf window-sizes state-config time-step migration-time host vms]
  {:pre [(posnum? step)
         (posnum? otf)
         (coll? window-sizes)
         (coll? state-config)
         (not-negnum? time-step)
         (not-negnum? migration-time)
         (map? host)
         (coll? vms)]
   :post [(boolean? %)]}
  (let [utilization (host-utilization-history host vms)
        total-time (count utilization)
        min-window-size (apply min window-sizes)
        max-window-size (apply max window-sizes)
        state-vector (build-state-vector state-config utilization)
        state (current-state state-vector)
        selected-windows (multisize-estimation/select-window
                           @state-variances @state-acceptable-variances window-sizes)
        p (multisize-estimation/select-best-estimates @state-estimate-windows selected-windows)]
    (do
      (swap! state-request-windows multisize-estimation/update-request-windows
             max-window-size @state-previous-state state)
      (swap! state-estimate-windows multisize-estimation/update-estimate-windows
             @state-request-windows @state-previous-state)
      (swap! state-variances multisize-estimation/update-variances
             @state-estimate-windows @state-previous-state)
      (swap! state-acceptable-variances multisize-estimation/update-acceptable-variances
             @state-estimate-windows @state-previous-state)
      (reset! state-previous-state state)

      (swap! state-selected-window-history multisize-estimation/update-selected-window-history
             selected-windows)
      (swap! state-best-estimate-history multisize-estimation/update-best-estimate-history p)
      (swap! state-time-history conj total-time)

      (if (>= total-time 30)
        (let [
              state-history (utilization-to-states state-config utilization)
              time-in-states total-time
              time-in-state-n (time-in-state-n state-config state-history)

              ls (if (= 1 (count state-config))
                   l-probabilities-2/ls
                   l-probabilities-3/ls)]
          (if (every? #{0} (nth p state))
            false
            (let [policy (bruteforce/optimize step 1.0 otf (/ migration-time time-step) ls p state-vector
                                              time-in-states time-in-state-n)
                  command (issue-command-deterministic policy)]
              command)))
        false))))
    """
    min_window_size = min(window_sizes)
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
        pass
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
