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

import neat.locals.underload.trivial as trivial

import logging
logging.disable(logging.CRITICAL)


class Trivial(TestCase):

    @qc(10)
    def always_underloaded_factory(
        time_step=int_(min=0, max=10),
        migration_time=float_(min=0, max=10),
        utilization=list_(of=float)
    ):
        alg = trivial.always_underloaded_factory(time_step, migration_time, {})
        assert alg(utilization) == (True, {})

    def test_threshold_factory(self):
        alg = trivial.threshold_factory(300, 20., {'threshold': 0.5})
        self.assertEqual(alg([]), (False, {}))
        self.assertEqual(alg([0.0, 0.0]), (True, {}))
        self.assertEqual(alg([0.0, 0.4]), (True, {}))
        self.assertEqual(alg([0.0, 0.5]), (True, {}))
        self.assertEqual(alg([0.0, 0.6]), (False, {}))
        self.assertEqual(alg([0.0, 1.0]), (False, {}))

    def test_last_n_average_threshold_factory(self):
        alg = trivial.last_n_average_threshold_factory(
            300, 20., {'threshold': 0.5,
                       'n': 2})
        self.assertEqual(alg([]), (False, {}))
        self.assertEqual(alg([0.0, 0.0]), (True, {}))
        self.assertEqual(alg([0.0, 0.4]), (True, {}))
        self.assertEqual(alg([0.0, 0.5]), (True, {}))
        self.assertEqual(alg([0.0, 0.6]), (True, {}))
        self.assertEqual(alg([0.0, 1.0]), (True, {}))
        self.assertEqual(alg([0.2, 1.0]), (False, {}))
        self.assertEqual(alg([0.0, 0.2, 1.0]), (False, {}))
        self.assertEqual(alg([0.0, 1.0, 1.0]), (False, {}))
        self.assertEqual(alg([0.0, 0.6, 0.6]), (False, {}))

        alg = trivial.last_n_average_threshold_factory(
            300, 20., {'threshold': 0.5,
                       'n': 3})
        self.assertEqual(alg([0.0, 0.6, 0.6]), (True, {}))

    def test_threshold(self):
        self.assertEqual(trivial.threshold(0.5, []), False)
        self.assertEqual(trivial.threshold(0.5, [0.0, 0.0]), True)
        self.assertEqual(trivial.threshold(0.5, [0.0, 0.4]), True)
        self.assertEqual(trivial.threshold(0.5, [0.0, 0.5]), True)
        self.assertEqual(trivial.threshold(0.5, [0.0, 0.6]), False)
        self.assertEqual(trivial.threshold(0.5, [0.0, 1.0]), False)

    def test_last_n_average_threshold(self):
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, []), False)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 0.0]), True)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 0.4]), True)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 0.5]), True)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 0.6]), True)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 1.0]), True)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.2, 1.0]), False)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 0.2, 1.0]), False)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 1.0, 1.0]), False)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 2, [0.0, 0.6, 0.6]), False)
        self.assertEqual(trivial.last_n_average_threshold(
                0.5, 3, [0.0, 0.6, 0.6]), True)
