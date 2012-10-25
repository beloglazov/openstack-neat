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

import operator

import neat.locals.overload.mhod.nlp as nlp

import logging
logging.disable(logging.CRITICAL)


class Nlp(TestCase):

    def test_build_objective(self):
        with MockTransaction:
            state_vector = [1, 0]
            p = [[-0.1, 0.1],
                 [0.3, -0.3]]
            m1 = mock('m1')
            m2 = mock('m2')
            m = [m1, m2]
            container = mock('function container')
            expect(container).l0(state_vector, p, m).and_return(2).once()
            expect(container).l1(state_vector, p, m).and_return(3).once()
            ls = [container.l0, container.l1]

            objective = nlp.build_objective(ls, state_vector, p)

            self.assertTrue(hasattr(objective, '__call__'))
            self.assertEqual(objective(m1, m2), 5)

    def test_build_constraint(self):
        with MockTransaction:
            otf = 0.05
            migration_time = 20.
            state_vector = [1, 0]
            p = [[-0.1, 0.1],
                 [0.3, -0.3]]
            m1 = mock('m1')
            m2 = mock('m2')
            m = [m1, m2]
            container = mock('function container')
            expect(container).l0(state_vector, p, m).and_return(2).once()
            expect(container).l1(state_vector, p, m). \
                and_return(3).exactly(2).times()
            ls = [container.l0, container.l1]

            constraint = nlp.build_constraint(otf, migration_time,
                                              ls, state_vector, p, 0, 0)

            self.assertTrue(hasattr(constraint[0], '__call__'))
            assert constraint[1] is operator.le
            self.assertEqual(constraint[2], otf)
            self.assertEqual(constraint[0](m1, m2),
                             float(migration_time + 3) /
                             (migration_time + 5))
