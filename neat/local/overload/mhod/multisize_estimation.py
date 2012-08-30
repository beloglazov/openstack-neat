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

""" Multisize sliding window workload estimation functions.
"""

from contracts import contract
from neat.contracts_extra import *


@contract
def mean(data, window_size):
    """ Get the data mean according to the window size.

    :param data: A list of values.
     :type data: list(number)

    :param window_size: A window size.
     :type window_size: int,>0

    :return: The mean value.
     :rtype: float
    """
    return float(sum(data)) / window_size


@contract
def variance(data, window_size):
    """ Get the data variance according to the window size.

    :param data: A list of values.
     :type data: list(number)

    :param window_size: A window size.
     :type window_size: int,>0

    :return: The variance value.
     :rtype: float
    """
    m = mean(data, window_size)
    return float(sum((x - m) ** 2 for x in data)) / (window_size - 1)


@contract
def acceptable_variance(probability, window_size):
    """ Get the acceptable variance.

    :param probability: The probability to use.
     :type probability: float,>=0

    :param window_size: A window size.
     :type window_size: int,>0

    :return: The acceptable variance.
     :rtype: float
    """
    return float(probability * (1 - probability)) / window_size


@contract
def estimate_probability(data, window_size, state):
    """ Get the estimated probability.

    :param data: A list of data values.
     :type data: list(number)

    :param window_size: The window size.
     :type window_size: int,>0

    :param state: The current state.
     :type state: int,>=0

    :return: The estimated probability.
     :rtype: float,>=0
    """
    return float(data.count(state)) / window_size


@contract
def update_request_windows(request_windows, max_window_size, previous_state, current_state):
    """ Update and return the updated request windows.
(defn update-request-windows [request-windows max-window-size previous-state current-state]
  {:pre [(vector? request-windows)
         (posnum? max-window-size)
         (not-negnum? previous-state)
         (not-negnum? current-state)]
   :post [(coll? %)]}
  (let [window (get request-windows previous-state)]
    (assoc request-windows previous-state
           (conj (take (dec max-window-size) window) current-state))))

    :param request_windows: The previous request windows.
     :type request_windows: list(int)

    :param max_window_size: The maximum window size.
     :type max_window_size: int

    :param previous_state: The previous state.
     :type previous_state: int

    :param current_state: The current state.
     :type current_state: int

    :return: The updated request windows.
     :rtype: list(int)
    """
    window = request_windows[previous_state]
    request_windows[previous_state]
