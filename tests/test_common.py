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
import shutil
import libvirt

import neat.common as common

import logging
logging.disable(logging.CRITICAL)


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

    @qc(10)
    def build_local_vm_path(
        x=str_(of='abc123_-/')
    ):
        assert common.build_local_vm_path(x) == os.path.join(x, 'vms')

    @qc(10)
    def build_local_host_path(
        x=str_(of='abc123_-/')
    ):
        assert common.build_local_host_path(x) == os.path.join(x, 'host')

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
            expect(connection).getInfo().and_return([0, 0, 0, x]).once()
            assert common.physical_cpu_mhz(connection) == x

    @qc(10)
    def physical_cpu_mhz_total(x=int_(min=0, max=8), y=int_(min=0, max=8)):
        with MockTransaction:
            connection = libvirt.virConnect()
            expect(common).physical_cpu_count(connection). \
                and_return(x).once()
            expect(common).physical_cpu_mhz(connection). \
                and_return(y).once()
            assert common.physical_cpu_mhz_total(connection) == x * y

    def test_frange(self):
        self.assertEqual([round(x, 1) for x in common.frange(0, 1.0, 0.5)],
                         [0.0, 0.5, 1.0])
        self.assertEqual([round(x, 1) for x in common.frange(0, 1.0, 0.2)],
                         [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

    def test_init_logging(self):
        log_dir = os.path.join(
            os.path.dirname(__file__), 'resources', 'log')
        log_file = 'test.log'
        log_path = os.path.join(log_dir, log_file)

        with MockTransaction:
            logging.root = mock('root')
            expect(logging).disable(logging.CRITICAL).once()
            expect(logging.root).setLevel.never()
            expect(logging.root).addHandler.never()
            assert common.init_logging(log_dir, log_file, 0)

        with MockTransaction:
            shutil.rmtree(log_dir, True)
            logging.root = mock('root')
            expect(logging).disable.never()
            expect(logging.root).setLevel(logging.WARNING).once()
            handler = mock('handler')
            expect(logging).FileHandler(log_path).and_return(handler).once()
            expect(handler).setFormatter.and_return(True).once()
            expect(logging).Formatter(
                '%(asctime)s %(levelname)-8s %(name)s %(message)s').once()
            expect(logging.root).addHandler.once()
            assert common.init_logging(log_dir, log_file, 1)
            assert os.access(log_dir, os.W_OK)

        with MockTransaction:
            logging.root = mock('root')
            expect(logging).disable.never()
            expect(logging.root).setLevel(logging.INFO).once()
            handler = mock('handler')
            expect(logging).FileHandler(log_path).and_return(handler).once()
            expect(handler).setFormatter.and_return(True).once()
            expect(logging).Formatter(
                '%(asctime)s %(levelname)-8s %(name)s %(message)s').once()
            expect(logging.root).addHandler.once()
            assert common.init_logging(log_dir, log_file, 2)
            assert os.access(log_dir, os.W_OK)

        with MockTransaction:
            logging.root = mock('root')
            expect(logging).disable.never()
            expect(logging.root).setLevel(logging.DEBUG).once()
            handler = mock('handler')
            expect(logging).FileHandler(log_path).and_return(handler).once()
            expect(handler).setFormatter.and_return(True).once()
            expect(logging).Formatter(
                '%(asctime)s %(levelname)-8s %(name)s %(message)s').once()
            expect(logging.root).addHandler.once()
            assert common.init_logging(log_dir, log_file, 3)
            assert os.access(log_dir, os.W_OK)

        shutil.rmtree(log_dir, True)

    def test_call_function_by_name(self):
        with MockTransaction:
            arg1 = 'a'
            arg2 = 'b'
            expect(common).func_to_call(arg1, arg2).and_return('res').once()
            assert common.call_function_by_name('neat.common.func_to_call',
                                                [arg1, arg2]) == 'res'

    def test_parse_parameters(self):
        params = '{"param1": 0.56, "param2": "abc"}'
        self.assertEqual(common.parse_parameters(params), {'param1': 0.56,
                                                           'param2': 'abc'})

    def test_parse_compute_hosts(self):
        assert common.parse_compute_hosts('') == []
        assert common.parse_compute_hosts('test1, test2') == \
            ['test1', 'test2']
        assert common.parse_compute_hosts('t1,,  t2 , t3') == \
            ['t1', 't2', 't3']

    @qc(10)
    def calculate_migration_time(
        data=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=int_(min=1, max=1000),
            min_length=1, max_length=10
        ),
        bandwidth=float_(min=1., max=100.)
    ):
        ram = data.values()
        migration_time = float(sum(ram)) / len(ram) / bandwidth
        assert common.calculate_migration_time(data, bandwidth) == \
            migration_time
