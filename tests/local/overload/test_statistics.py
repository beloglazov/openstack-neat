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

import neat.local.overload.statistics as stats


class Statistics(TestCase):

    def test_loess_parameter_estimates(self):
        data = [1.05, 1.09, 1.07, 1.12, 1.02, 1.18, 1.15, 1.04, 1.1, 1.16, 1.08]
        # print stats.loess_parameter_estimates(data)

    def test_tricube_weights(self):
        for actual, expected in zip(
                stats.tricube_weights(5),
                [1.492, 1.492, 1.492, 1.048, 1.000]):
            self.assertAlmostEqual(actual, expected, 2)

        for actual, expected in zip(
                stats.tricube_weights(10),
                [6.736, 6.736, 6.736, 2.869, 1.758, 1.317, 1.119, 1.033, 1.004, 1.000]):
            self.assertAlmostEqual(actual, expected, 2)

    def test_tricube_bisquare_weights(self):
        for actual, expected in zip(
                stats.tricube_bisquare_weights([1., 1., 2., 2., 4., 6., 9.]),
                [3.035, 3.035, 3.035, 1.579, 1.417, 1.802, 5.224]):
            self.assertAlmostEqual(actual, expected, 2)
