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


class Otf(TestCase):

    @qc
    def overloading_steps(
        x=list_(
            of=float_(min=0.0, max=2.0),
            min_length=0, max_length=10
        )
    ):
        assert otf.overloading_steps(x) == len(filter(lambda y: y >= 1.0, x))

    def test_otf(self):
        self.assertTrue(otf.otf(0.5, [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertFalse(otf.otf(0.5, [0.9, 0.8, 1.1, 1.2, 0.3]))

    def test_otf_limit(self):
        self.assertFalse(otf.otf_limit(0.5, 10, [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertFalse(otf.otf_limit(0.5, 10, [0.9, 0.8, 1.1, 1.2, 0.3]))
        self.assertTrue(otf.otf_limit(0.5, 5, [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertFalse(otf.otf_limit(0.5, 5, [0.9, 0.8, 1.1, 1.2, 0.3]))

    def test_otf_migration_time(self):
        self.assertTrue(otf.otf_migration_time(
            0.5, 100., [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertTrue(otf.otf_migration_time(
            0.5, 100., [0.9, 0.8, 1.1, 1.2, 0.3]))
        self.assertTrue(otf.otf_migration_time(
            0.5, 1., [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertFalse(otf.otf_migration_time(
            0.5, 1., [0.9, 0.8, 1.1, 1.2, 0.3]))

    def test_otf_limit_migration_time(self):
        self.assertFalse(otf.otf_limit_migration_time(
            0.5, 10, 100., [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertFalse(otf.otf_limit_migration_time(
            0.5, 10, 100., [0.9, 0.8, 1.1, 1.2, 0.3]))
        self.assertFalse(otf.otf_limit_migration_time(
            0.5, 10, 1., [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertFalse(otf.otf_limit_migration_time(
            0.5, 10, 1., [0.9, 0.8, 1.1, 1.2, 0.3]))
        self.assertTrue(otf.otf_limit_migration_time(
            0.5, 5, 100., [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertTrue(otf.otf_limit_migration_time(
            0.5, 5, 100., [0.9, 0.8, 1.1, 1.2, 0.3]))
        self.assertTrue(otf.otf_limit_migration_time(
            0.5, 5, 1., [0.9, 0.8, 1.1, 1.2, 1.3]))
        self.assertFalse(otf.otf_limit_migration_time(
            0.5, 5, 1., [0.9, 0.8, 1.1, 1.2, 0.3]))

    def test_otf_factory(self):
        alg = otf.otf_factory(
            300, 20., {'threshold': 0.5})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))

    def test_otf_limit_factory(self):
        alg = otf.otf_limit_factory(
            300, 20., {'threshold': 0.5, 'limit': 10})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (False, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))

        alg = otf.otf_limit_factory(
            300, 20., {'threshold': 0.5, 'limit': 5})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))

    def test_otf_migration_time_factory(self):
        alg = otf.otf_migration_time_factory(
            30, 3000., {'threshold': 0.5})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (True, {}))

        alg = otf.otf_migration_time_factory(
            300, 1., {'threshold': 0.5})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))

    def test_otf_limit_migration_time_factory(self):
        alg = otf.otf_limit_migration_time_factory(
            30, 3000., {'threshold': 0.5, 'limit': 10})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (False, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))

        alg = otf.otf_limit_migration_time_factory(
            300, 1., {'threshold': 0.5, 'limit': 10})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (False, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))

        alg = otf.otf_limit_migration_time_factory(
            30, 3000., {'threshold': 0.5, 'limit': 5})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (True, {}))

        alg = otf.otf_limit_migration_time_factory(
            300, 1., {'threshold': 0.5, 'limit': 5})
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 1.3]), (True, {}))
        self.assertEqual(alg([0.9, 0.8, 1.1, 1.2, 0.3]), (False, {}))
