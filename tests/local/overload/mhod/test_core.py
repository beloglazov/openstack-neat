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

import neat.local.overload.mhod.core as core


class Core(TestCase):

    def test_init_state(self):
        state = core.init_state([20, 40], 2)
        self.assertEquals(state['previous_state'], 0)
        self.assertTrue('request_windows' in state)
        self.assertTrue('estimate_windows' in state)
        self.assertTrue('variances' in state)
        self.assertTrue('acceptable_variances' in state)
