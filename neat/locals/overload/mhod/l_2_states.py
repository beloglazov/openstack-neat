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

""" L functions for the 2 state configuration of the MHOD algorithm.
"""

from contracts import contract
from neat.contracts_extra import *

import logging
log = logging.getLogger(__name__)


@contract
def l0(p_initial, p_matrix, m):
    """ Compute the L0 function.

    :param p_initial: The initial state distribution.
     :type p_initial: list(number)

    :param p_matrix: A matrix of transition probabilities.
     :type p_matrix: list(list(number))

    :param m: The m values.
     :type m: list(number)

    :return: The value of the L0 function.
     :rtype: number
    """
    p0 = p_initial[0]
    p1 = p_initial[1]
    p00 = p_matrix[0][0]
    p01 = p_matrix[0][1]
    p10 = p_matrix[1][0]
    p11 = p_matrix[1][1]
    m0 = m[0]
    m1 = m[1]
    return ((p0 * (-1 * m1 * p11 + p11 - 1) + (m1 * p1 - p1) * p10) /
            (p00 * (m1 * (p11 - m0 * p11) - p11 + m0 * (p11 - 1) + 1) -
             m1 * p11 + p11 + (m1 * (m0 * p01 - p01) - m0 * p01 + p01) *
             p10 - 1))


@contract
def l1(p_initial, p_matrix, m):
    """ Compute the L1 function.

    :param p_initial: The initial state distribution.
     :type p_initial: list(number)

    :param p_matrix: A matrix of transition probabilities.
     :type p_matrix: list(list(number))

    :param m: The m values.
     :type m: list(number)

    :return: The value of the L1 function.
     :rtype: number
    """
    p0 = p_initial[0]
    p1 = p_initial[1]
    p00 = p_matrix[0][0]
    p01 = p_matrix[0][1]
    p10 = p_matrix[1][0]
    p11 = p_matrix[1][1]
    m0 = m[0]
    m1 = m[1]
    return (-1 * (p00 * (m0 * p1 - p1) + p1 + p0 * (p01 - m0 * p01)) /
            (p00 * (m1 * (p11 - m0 * p11) - p11 + m0 * (p11 - 1) + 1) -
             m1 * p11 + p11 + (m1 * (m0 * p01 - p01) - m0 * p01 + p01) *
             p10 - 1))


ls = [l0, l1]
