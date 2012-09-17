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

import neat.local.vm_selection.algorithms as selection


class Selection(TestCase):

    @qc(10)
    def minimum_migration_time_factory(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=int_(min=0, max=3000),
            min_length=1, max_length=5
        )
    ):
        alg = selection.minimum_migration_time_factory(300, 20, dict())
        values = x.values()
        vm_index = values.index(min(values))
        vm = x.keys()[vm_index]
        assert alg(dict(), x) == (vm, {})

    @qc(10)
    def minimum_utilization_factory(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=0, max=3000), min_length=1, max_length=10),
            min_length=1, max_length=5
        )
    ):
        alg = selection.minimum_utilization_factory(300, 20, dict())
        last_utilization = []
        for utilization in x.values():
            last_utilization.append(utilization[-1])
        vm_index = last_utilization.index(min(last_utilization))
        vm = x.keys()[vm_index]
        assert alg(x, dict()) == (vm, {})

    @qc(10)
    def random_factory(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=0, max=3000), min_length=0, max_length=10),
            min_length=1, max_length=3
        )
    ):
        with MockTransaction:
            alg = selection.random_factory(300, 20, dict())
            vm = x.keys()[random.randrange(len(x))]
            expect(selection).choice(x.keys()).and_return(vm).once()
            assert alg(x, dict()) == (vm, {})

    @qc(10)
    def minimum_migration_time(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=int_(min=0, max=3000),
            min_length=1, max_length=5
        )
    ):
        values = x.values()
        vm_index = values.index(min(values))
        vm = x.keys()[vm_index]
        assert selection.minimum_migration_time(x) == vm

    @qc(10)
    def minimum_utilization(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=0, max=3000), min_length=1, max_length=10),
            min_length=1, max_length=5
        )
    ):
        last_utilization = []
        for utilization in x.values():
            last_utilization.append(utilization[-1])
        vm_index = last_utilization.index(min(last_utilization))
        vm = x.keys()[vm_index]
        assert selection.minimum_utilization(x) == vm

    @qc(10)
    def random(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=0, max=3000), min_length=0, max_length=10),
            min_length=1, max_length=3
        )
    ):
        with MockTransaction:
            vm = x.keys()[random.randrange(len(x))]
            expect(selection).choice(x.keys()).and_return(vm).once()
            assert selection.random(x) == vm


    # def test_threshold_factory(self):
    #     alg = trivial.threshold_factory(300, 20, {'threshold': 0.5})
    #     self.assertEqual(alg([]), (False, {}))
    #     self.assertEqual(alg([0.0, 0.0]), (True, {}))
    #     self.assertEqual(alg([0.0, 0.4]), (True, {}))
    #     self.assertEqual(alg([0.0, 0.5]), (True, {}))
    #     self.assertEqual(alg([0.0, 0.6]), (False, {}))
    #     self.assertEqual(alg([0.0, 1.0]), (False, {}))
