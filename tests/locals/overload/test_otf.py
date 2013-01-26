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

import neat.locals.overload.otf as otf

import logging
logging.disable(logging.CRITICAL)


class Otf(TestCase):

    def test_otf(self):
        state = {'overload': 0, 'total': 0}

        decision, state = otf.otf(0.5, 1.0, 4, 1., 
                                  [0.9], state)
        self.assertEqual(state, {'overload': 0, 'total': 1})
        self.assertFalse(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 1., 
                                  [0.9, 1.3], state)
        self.assertEqual(state, {'overload': 1, 'total': 2})
        self.assertFalse(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 1., 
                                  [0.9, 1.3, 1.1], state)
        self.assertEqual(state, {'overload': 2, 'total': 3})
        self.assertFalse(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 1., 
                                  [0.9, 1.3, 1.1, 1.2], state)
        self.assertEqual(state, {'overload': 3, 'total': 4})
        self.assertTrue(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 100., 
                                  [0.9, 1.3, 1.1, 1.2, 0.3], state)
        self.assertEqual(state, {'overload': 3, 'total': 5})
        self.assertFalse(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 1., 
                                  [0.9, 1.3, 1.1, 1.2, 1.3], state)
        self.assertEqual(state, {'overload': 4, 'total': 6})
        self.assertTrue(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 1., 
                                  [0.9, 1.3, 1.1, 1.2, 0.3, 0.2], state)
        self.assertEqual(state, {'overload': 4, 'total': 7})
        self.assertFalse(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 0., 
                                  [0.9, 1.3, 1.1, 1.2, 0.3, 0.2, 0.1], state)
        self.assertEqual(state, {'overload': 4, 'total': 8})
        self.assertFalse(decision)

        decision, state = otf.otf(0.5, 1.0, 4, 0., 
                                  [0.9, 1.3, 1.1, 1.2, 0.3, 0.2, 0.1, 0.1], state)
        self.assertEqual(state, {'overload': 4, 'total': 9})
        self.assertFalse(decision)


    def test_otf_factory(self):
        alg = otf.otf_factory(30, 0., 
                              {'otf': 0.5, 'threshold': 1.0, 'limit': 4})

        decision, state = alg([0.9], None)
        self.assertEqual(state, {'overload': 0, 'total': 1})
        self.assertFalse(decision)

        decision, state = alg([0.9, 1.3], state)
        self.assertEqual(state, {'overload': 1, 'total': 2})
        self.assertFalse(decision)

        decision, state = alg([0.9, 1.3, 1.1], state)
        self.assertEqual(state, {'overload': 2, 'total': 3})
        self.assertFalse(decision)

        decision, state = alg([0.9, 1.3, 1.1, 1.2], state)
        self.assertEqual(state, {'overload': 3, 'total': 4})
        self.assertTrue(decision)

        decision, state = alg([0.9, 1.3, 1.1, 1.2, 0.3], state)
        self.assertEqual(state, {'overload': 3, 'total': 5})
        self.assertFalse(decision)

        decision, state = alg([0.9, 1.3, 1.1, 1.2, 1.3], state)
        self.assertEqual(state, {'overload': 4, 'total': 6})
        self.assertTrue(decision)

        decision, state = alg([0.9, 1.3, 1.1, 1.2, 0.3, 0.2], state)
        self.assertEqual(state, {'overload': 4, 'total': 7})
        self.assertFalse(decision)

        decision, state = alg([0.9, 1.3, 1.1, 1.2, 0.3, 0.2, 0.1], state)
        self.assertEqual(state, {'overload': 4, 'total': 8})
        self.assertFalse(decision)

        decision, state = alg([0.9, 1.3, 1.1, 1.2, 0.3, 0.2, 0.1, 0.1], state)
        self.assertEqual(state, {'overload': 4, 'total': 9})
        self.assertFalse(decision)
