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
from itertools import islice

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
     :type probability: number,>=0,<=1

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
def update_request_windows(request_windows, previous_state, current_state):
    """ Update and return the updated request windows.

    :param request_windows: The previous request windows.
     :type request_windows: list(deque)

    :param previous_state: The previous state.
     :type previous_state: int,>=0

    :param current_state: The current state.
     :type current_state: int,>=0

    :return: The updated request windows.
     :rtype: list(deque)
    """
    request_windows[previous_state].append(current_state)
    return request_windows


@contract
def update_estimate_windows(estimate_windows, request_windows, previous_state):
    """ Update and return the updated estimate windows.

    :param estimate_windows: The previous estimate windows.
     :type estimate_windows: list(list(dict))

    :param request_windows: The current request windows.
     :type request_windows: list(deque)

    :param previous_state: The previous state.
     :type previous_state: int,>=0

    :return: The updated estimate windows.
     :rtype: list(list(dict))
    """
    request_window = request_windows[previous_state]
    for state, estimate_window in enumerate(estimate_windows[previous_state]):
        for window_size, estimates in estimate_window.items():
            slice_from = len(request_window) - window_size
            if slice_from < 0:
                slice_from = 0
            estimates.append(
                estimate_probability(
                    list(islice(request_window, slice_from, None)),
                    window_size, state))
    return estimate_windows


@contract
def update_variances(variances, estimate_windows, previous_state):
    """ Updated and return the updated variances.

    :param variances: The previous variances.
     :type variances: list(list(dict))

    :param estimate_windows: The current estimate windows.
     :type estimate_windows: list(list(dict))

    :param previous_state: The previous state.
     :type previous_state: int,>=0

    :return: The updated variances.
     :rtype: list(list(dict))
    """
    estimate_window = estimate_windows[previous_state]
    for state, variance_map in enumerate(variances[previous_state]):
        for window_size in variance_map:
            estimates = estimate_window[state][window_size]
            if len(estimates) < window_size:
                variance_map[window_size] = 1.0
            else:
                variance_map[window_size] = variance(list(estimates), window_size)
    return variances


@contract
def update_acceptable_variances(acceptable_variances, estimate_windows, previous_state):
    """ Update and return the updated acceptable variances.

    :param acceptable_variances: The previous acceptable variances.
     :type acceptable_variances: list(list(dict))

    :param estimate_windows: The current estimate windows.
     :type estimate_windows: list(list(dict))

    :param previous_state: The previous state.
     :type previous_state: int,>=0

    :return: The updated acceptable variances.
     :rtype: list(list(dict))
    """
    estimate_window = estimate_windows[previous_state]
    for state, acceptable_variance_map in enumerate(acceptable_variances[previous_state]):
        for window_size in acceptable_variance_map:
            estimates = estimate_window[state][window_size]
            acceptable_variance_map[window_size] = acceptable_variance(estimates[-1], window_size)
    return acceptable_variances
