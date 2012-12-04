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

import neat.locals.overload.trivial as trivial

import logging
logging.disable(logging.CRITICAL)


class Trivial(TestCase):

    @qc(10)
    def never_overloaded_factory(
        time_step=int_(min=0, max=10),
        migration_time=float_(min=0, max=10),
        utilization=list_(of=float)
    ):
        alg = trivial.never_overloaded_factory(time_step, migration_time, {})
        assert alg(utilization) == (False, {})

    def test_threshold_factory(self):
        alg = trivial.threshold_factory(300, 20., {'threshold': 0.5})
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.6]), (True, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.5]), (False, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))
        self.assertEquals(alg([]), (False, {}))

    def test_last_n_average_threshold_factory(self):
        alg = trivial.last_n_average_threshold_factory(
            300, 20., {'threshold': 0.5, 'n': 1})
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.6]), (True, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.5]), (False, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))
        self.assertEquals(alg([]), (False, {}))

        alg = trivial.last_n_average_threshold_factory(
            300, 20., {'threshold': 0.5, 'n': 2})
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.6]), (True, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 1.2, 0.4]), (True, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 0.4, 0.5]), (False, {}))
        self.assertEquals(alg([0.9, 0.8, 1.1, 0.2, 0.3]), (False, {}))
        self.assertEquals(alg([]), (False, {}))

    def test_threshold(self):
        self.assertTrue(trivial.threshold(0.5, [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertTrue(trivial.threshold(0.5, [0.9, 0.8, 1.1, 1.2, 0.6]))
        self.assertFalse(trivial.threshold(0.5, [0.9, 0.8, 1.1, 1.2, 0.5]))
        self.assertFalse(trivial.threshold(0.5, [0.9, 0.8, 1.1, 1.2, 0.3]))
        self.assertFalse(trivial.threshold(0.5, []))

    def test_last_n_average_threshold(self):
        self.assertTrue(trivial.last_n_average_threshold(
                0.5, 1, [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertTrue(trivial.last_n_average_threshold(
                0.5, 1, [0.9, 0.8, 1.1, 1.2, 0.6]))
        self.assertFalse(trivial.last_n_average_threshold(
                0.5, 1, [0.9, 0.8, 1.1, 1.2, 0.5]))
        self.assertFalse(trivial.last_n_average_threshold(
                0.5, 1, [0.9, 0.8, 1.1, 1.2, 0.3]))
        self.assertFalse(trivial.last_n_average_threshold(
                0.5, 1, []))

        self.assertTrue(trivial.last_n_average_threshold(
                0.5, 2, [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertTrue(trivial.last_n_average_threshold(
                0.5, 2, [0.9, 0.8, 1.1, 1.2, 0.6]))
        self.assertTrue(trivial.last_n_average_threshold(
                0.5, 2, [0.9, 0.8, 1.1, 1.2, 0.4]))
        self.assertFalse(trivial.last_n_average_threshold(
                0.5, 2, [0.9, 0.8, 1.1, 0.4, 0.5]))
        self.assertFalse(trivial.last_n_average_threshold(
                0.5, 2, [0.9, 0.8, 1.1, 0.2, 0.3]))
        self.assertFalse(trivial.last_n_average_threshold(0.5, 2, []))
