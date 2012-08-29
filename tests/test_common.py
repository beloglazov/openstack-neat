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

import os
import libvirt

import neat.common as common


class Common(TestCase):

    @qc(10)
    def start(iterations=int_(0, 10)):
        with MockTransaction:
            config = {'option': 'value'}
            state = {'property': 'value'}
            fn = mock('function container')
            expect(fn).init_state(any_dict).and_return(state).once()
            expect(fn).execute(any_dict, any_dict). \
                and_return(state).exactly(iterations).times()
            assert common.start(fn.init_state,
                                fn.execute,
                                config,
                                0,
                                iterations) == state

    @qc
    def build_local_vm_path(
        x=str_(of='abc123_-/')
    ):
        assert common.build_local_vm_path(x) == os.path.join(x, 'vms')

    @qc(10)
    def physical_cpu_count(x=int_(min=0, max=8)):
        with MockTransaction:
            connection = libvirt.virConnect()
            expect(connection).getInfo().and_return([0, 0, x]).once()
            assert common.physical_cpu_count(connection) == x

    @qc(10)
    def physical_cpu_mhz(x=int_(min=0, max=8)):
        with MockTransaction:
            connection = libvirt.virConnect()
            expect(connection).getInfo().and_return([0, x, 0]).once()
            assert common.physical_cpu_mhz(connection) == x
