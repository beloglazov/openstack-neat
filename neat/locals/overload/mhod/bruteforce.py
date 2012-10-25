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

import nlp
from neat.common import frange

import logging
log = logging.getLogger(__name__)


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


@contract
def optimize(step, limit, otf, migration_time, ls, p, state_vector,
             time_in_states, time_in_state_n):
    """ Solve a MHOD optimization problem.

    :param step: The step size for the bruteforce algorithm.
     :type step: number,>0

    :param limit: The maximum value of the variables.
     :type limit: number,>0

    :param otf: The OTF parameter.
     :type otf: number,>=0,<=1

    :param migration_time: The VM migration time in time steps.
     :type migration_time: float,>=0

    :param ls: L functions.
     :type ls: list(function)

    :param p: A matrix of transition probabilities.
     :type p: list(list(number))

    :param state_vector: A state vector.
     :type state_vector: list(int)

    :param time_in_states: The total time in all the states in time steps.
     :type time_in_states: number,>=0

    :param time_in_state_n: The total time in the state N in time steps.
     :type time_in_state_n: number,>=0

    :return: The solution of the problem.
     :rtype: list(number)
    """
    objective = nlp.build_objective(ls, state_vector, p)
    constraint = nlp.build_constraint(otf, migration_time, ls, state_vector,
                                      p, time_in_states, time_in_state_n)
    return solve2(objective, constraint, step, limit)
