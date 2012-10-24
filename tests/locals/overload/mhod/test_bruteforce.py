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

from mocktest import *
from pyqcy import *

from operator import le

import neat.locals.overload.mhod.bruteforce as b
import neat.locals.overload.mhod.nlp as nlp

import logging
logging.disable(logging.CRITICAL)


class Bruteforce(TestCase):

    def test_solve2(self):
        def fn1(x, y):
            return x + y

        def fn2(x, y):
            return 2 * x + y

        def fn3(x, y):
            return x - y

        def fn4(x, y):
            return x / y

        self.assertEqual([round(x, 1)
                          for x in b.solve2(fn1, (fn1, le, 10), 0.1, 1.0)],
                         [1.0, 1.0])
        self.assertEqual([round(x, 1)
                          for x in b.solve2(fn1, (fn1, le, 0.5), 0.1, 1.0)],
                         [0.0, 0.5])
        self.assertEqual([round(x, 1)
                          for x in b.solve2(fn2, (fn1, le, 0.5), 0.1, 1.0)],
                         [0.5, 0.0])
        self.assertEqual([round(x, 1)
                          for x in b.solve2(fn3, (fn3, le, 10), 0.1, 1.0)],
                         [1.0, 0.0])
        self.assertEqual([round(x, 1)
                          for x in b.solve2(fn4, (fn4, le, 10), 0.1, 1.0)],
                         [1.0, 0.1])

    def test_optimize(self):
        with MockTransaction:
            step = 0.1
            limit = 1
            otf = 0.3
            migration_time = 20.
            ls = [lambda x: x, lambda x: x]
            p = [[0, 1]]
            state_vector = [0, 1]
            time_in_states = 10
            time_in_state_n = 5
            objective = mock('objective')
            constraint = mock('constraint')
            solution = [1, 2, 3]
            expect(nlp).build_objective(ls, state_vector, p). \
                and_return(objective).once()
            expect(nlp).build_constraint(
                otf, migration_time, ls, state_vector,
                p, time_in_states, time_in_state_n). \
                and_return(constraint).once()
            expect(b).solve2(objective, constraint, step, limit). \
                and_return(solution).once()
            self.assertEqual(
                b.optimize(step, limit, otf, migration_time, ls,
                           p, state_vector, time_in_states, time_in_state_n),
                solution)
