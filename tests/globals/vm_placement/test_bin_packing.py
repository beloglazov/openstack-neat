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

import neat.globals.vm_placement.bin_packing as algs


class BinPacking(TestCase):

    pass
    # @qc(10)
    # def minimum_migration_time_factory(
    #     x=dict_(
    #         keys=str_(of='abc123-', min_length=36, max_length=36),
    #         values=int_(min=0, max=3000),
    #         min_length=1, max_length=5
    #     )
    # ):
    #     alg = selection.minimum_migration_time_factory(300, 20, dict())
    #     values = x.values()
    #     vm_index = values.index(min(values))
    #     vm = x.keys()[vm_index]
    #     assert alg(dict(), x) == (vm, {})

    # @qc(10)
    # def minimum_migration_time(
    #     x=dict_(
    #         keys=str_(of='abc123-', min_length=36, max_length=36),
    #         values=int_(min=0, max=3000),
    #         min_length=1, max_length=5
    #     )
    # ):
    #     values = x.values()
    #     vm_index = values.index(min(values))
    #     vm = x.keys()[vm_index]
    #     assert selection.minimum_migration_time(x) == vm
