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

from collections import deque

import neat.local.overload.mhod.multisize_estimation as m


time_limit = 30
workloads = [{'until': 15,
              'transitions': [[0.2, 0.8],
                              [1.0, 0.0]]},
             {'until': 30,
              'transitions': [[0.5, 0.5],
                              [1.0, 0.0]]}]
window_sizes = [2, 4, 6]


class Multisize(TestCase):

    def test_mean(self):
        self.assertEqual(m.mean([], 100), 0.0)
        self.assertEqual(m.mean([0], 100), 0.0)
        self.assertEqual(m.mean([0, 0], 100), 0.0)
        self.assertEqual(m.mean([1, 1], 100), 0.02)
        self.assertEqual(m.mean([0, 1], 100), 0.01)
        self.assertEqual(m.mean([1, 2, 3, 4, 5], 100), 0.15)

    def test_variance(self):
        self.assertEqual(m.variance([], 100), 0.0)
        self.assertEqual(m.variance([0], 100), 0.0)
        self.assertEqual(m.variance([0, 0], 100), 0.0)
        self.assertAlmostEqual(m.variance([1, 1], 100), 0.0194020202)
        self.assertAlmostEqual(m.variance([0, 1], 100), 0.0099010101)
        self.assertAlmostEqual(m.variance([1, 2, 3, 4, 5], 100), 0.5112373737)
        self.assertAlmostEqual(m.variance([0, 0, 0, 1], 100), 0.0099030303)

    def test_acceptable_variance(self):
        self.assertAlmostEqual(m.acceptable_variance(0.2, 5), 0.032, 3)
        self.assertAlmostEqual(m.acceptable_variance(0.6, 15), 0.016, 3)

    def test_estimate_probability(self):
        self.assertEqual(
            m.estimate_probability([0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 100, 0), 0.08)
        self.assertEqual(
            m.estimate_probability([0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 100, 1), 0.02)
        self.assertEqual(
            m.estimate_probability([1, 1, 0, 0, 1, 1, 1, 1, 1, 1], 200, 0), 0.01)
        self.assertEqual(
            m.estimate_probability([1, 1, 0, 0, 1, 1, 1, 1, 1, 1], 200, 1), 0.04)

    def test_update_request_windows(self):
        windows = [[0, 0],
                   [1, 1]]

        self.assertEqual(m.update_request_windows(windows, 4, 0, 0), [[0, 0, 0],
                                                                      [1, 1]])
        self.assertEqual(m.update_request_windows(windows, 4, 0, 1), [[0, 0, 1],
                                                                      [1, 1]])
        self.assertEqual(m.update_request_windows(windows, 4, 1, 0), [[0, 0],
                                                                      [1, 1, 0]])
        self.assertEqual(m.update_request_windows(windows, 4, 1, 1), [[0, 0],
                                                                      [1, 1, 1]])

        self.assertEqual(m.update_request_windows(windows, 2, 0, 0), [[0, 0],
                                                                      [1, 1]])
        self.assertEqual(m.update_request_windows(windows, 2, 0, 1), [[0, 1],
                                                                      [1, 1]])
        self.assertEqual(m.update_request_windows(windows, 2, 1, 0), [[0, 0],
                                                                      [1, 0]])
        self.assertEqual(m.update_request_windows(windows, 2, 1, 1), [[0, 0],
                                                                      [1, 1]])

        windows = [[0, 0],
                   [1, 1],
                   [2, 2]]

        self.assertEqual(m.update_request_windows(windows, 4, 0, 0), [[0, 0, 0],
                                                                      [1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 4, 0, 1), [[0, 0, 1],
                                                                      [1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 4, 0, 2), [[0, 0, 2],
                                                                      [1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 4, 1, 0), [[0, 0],
                                                                      [1, 1, 0],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 4, 1, 1), [[0, 0],
                                                                      [1, 1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 4, 1, 2), [[0, 0],
                                                                      [1, 1, 2],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 4, 2, 0), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 2, 0]])
        self.assertEqual(m.update_request_windows(windows, 4, 2, 1), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 2, 1]])
        self.assertEqual(m.update_request_windows(windows, 4, 2, 2), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 2, 2]])

        self.assertEqual(m.update_request_windows(windows, 2, 0, 0), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 2, 0, 1), [[0, 1],
                                                                      [1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 2, 0, 2), [[0, 2],
                                                                      [1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 2, 1, 0), [[0, 0],
                                                                      [1, 0],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 2, 1, 1), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 2, 1, 2), [[0, 0],
                                                                      [1, 2],
                                                                      [2, 2]])
        self.assertEqual(m.update_request_windows(windows, 2, 2, 0), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 0]])
        self.assertEqual(m.update_request_windows(windows, 2, 2, 1), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 1]])
        self.assertEqual(m.update_request_windows(windows, 2, 2, 2), [[0, 0],
                                                                      [1, 1],
                                                                      [2, 2]])
