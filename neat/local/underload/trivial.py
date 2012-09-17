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
