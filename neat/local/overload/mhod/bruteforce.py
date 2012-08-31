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

""" Functions for solving NLP problems using the bruteforce method.
"""

from contracts import contract
from neat.contracts_extra import *

from neat.common import frange


@contract
def solve2(objective, constraint, step, limit):
    """ Solve a maximization problem for 2 states.

    :param objective: The objective function.
     :type objective: function

    :param constraint: A tuple representing the constraint.
     :type constraint: tuple(function, function, number)

    :param step: The step size.
     :type step: number,>0

    :param limit: The maximum value of the variables.
     :type limit: number,>0

    :return: The problem solution.
     :rtype: list(number)
    """
    res_best = 0
    solution = []
    for x in frange(0, limit, step):
        for y in frange(0, limit, step):
            try:
                res = objective(x, y)
                if res > res_best and \
                   constraint[1](constraint[0](x, y), constraint[2]):
                    res_best = res
                    solution = [x, y]
            except ZeroDivisionError:
                pass
    return solution
