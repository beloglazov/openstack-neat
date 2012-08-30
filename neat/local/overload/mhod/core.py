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

    :param state: The history of the host's CPU utilization.
     :type state: list(float)

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
