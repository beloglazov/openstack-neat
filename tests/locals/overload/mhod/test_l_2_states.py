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

import neat.locals.overload.mhod.l_2_states as l

import logging
logging.disable(logging.CRITICAL)


class L2States(TestCase):

    def test_l0(self):
        p = [[0.4, 0.6],
             [0.9, 0.1]]
        p0 = [1, 0]

        self.assertAlmostEqual(l.l0(p0, p, [0.2, 0.8]), 1.690, 3)
        self.assertAlmostEqual(l.l0(p0, p, [0.62, 0.38]), 1.404, 3)

    def test_l1(self):
        p = [[0.4, 0.6],
             [0.9, 0.1]]
        p0 = [1, 0]

        self.assertAlmostEqual(l.l1(p0, p, [0.2, 0.8]), 0.828, 3)
        self.assertAlmostEqual(l.l1(p0, p, [0.62, 0.38]), 0.341, 3)
