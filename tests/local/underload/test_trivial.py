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

import neat.local.underload.trivial as trivial


class Trivial(TestCase):

    def test_threshold_factory(self):
        alg = trivial.threshold_factory(300, 20, {'threshold': 0.5})
        self.assertEqual(alg([]), (False, {}))
        self.assertEqual(alg([0.0, 0.0]), (True, {}))
        self.assertEqual(alg([0.0, 0.4]), (True, {}))
        self.assertEqual(alg([0.0, 0.5]), (True, {}))
        self.assertEqual(alg([0.0, 0.6]), (False, {}))
        self.assertEqual(alg([0.0, 1.0]), (False, {}))

    def test_threshold(self):
        assert trivial.threshold(0.5, []) == False
        assert trivial.threshold(0.5, [0.0, 0.0]) == True
        assert trivial.threshold(0.5, [0.0, 0.4]) == True
        assert trivial.threshold(0.5, [0.0, 0.5]) == True
        assert trivial.threshold(0.5, [0.0, 0.6]) == False
        assert trivial.threshold(0.5, [0.0, 1.0]) == False
