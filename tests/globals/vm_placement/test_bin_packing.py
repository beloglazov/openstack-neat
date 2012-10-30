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

import neat.globals.vm_placement.bin_packing as packing

import logging
logging.disable(logging.CRITICAL)


class BinPacking(TestCase):

    def test_best_fit_decreasing_factory(self):
        alg = packing.best_fit_decreasing_factory(300, 20.,
                                                  {'cpu_threshold': 0.8,
                                                   'ram_threshold': 0.9,
                                                   'last_n_vm_cpu': 1})

        hosts_cpu_usage = {
            'host1': 200,
            'host2': 2200,
            'host3': 1200}
        hosts_cpu_total = {
            'host1': 4000,
            'host2': 4000,
            'host3': 4000}
        hosts_ram_usage = {
            'host1': 3276,
            'host2': 6348,
            'host3': 5324}
        hosts_ram_total = {
            'host1': 8192,
            'host2': 8192,
            'host3': 8192}
        inactive_hosts_cpu = {
            'host4': 3000,
            'host5': 1000,
            'host6': 2000}
        inactive_hosts_ram = {
            'host4': 4096,
            'host5': 1024,
            'host6': 2048}
        vms_cpu = {
            'vm1': [100, 1000],
            'vm2': [100, 1000],
            'vm3': [100, 1000]}
        vms_ram = {
            'vm1': 2048,
            'vm2': 4096,
            'vm3': 2048}

        self.assertEqual(alg(hosts_cpu_usage, hosts_cpu_total,
                             hosts_ram_usage, hosts_ram_total,
                             inactive_hosts_cpu, inactive_hosts_ram,
                             vms_cpu, vms_ram), ({
                                 'vm1': 'host6',
                                 'vm2': 'host1',
                                 'vm3': 'host3'}, {}))

    def test_get_available_resources(self):
        self.assertEqual(packing.get_available_resources(
            0.8,
            {'host1': 700, 'host2': 200}, {'host1': 1000, 'host2': 2000}),
            {'host1': 100, 'host2': 1400})

    def test_best_fit_decreasing(self):
        hosts_cpu = {
            'host1': 3000,
            'host2': 1000,
            'host3': 2000}
        hosts_ram = {
            'host1': 1024,
            'host2': 4096,
            'host3': 2048}
        inactive_hosts_cpu = {}
        inactive_hosts_ram = {}
        vms_cpu = {
            'vm1': [100, 2000],
            'vm2': [100, 1000],
            'vm3': [100, 3000]}
        vms_ram = {
            'vm1': 512,
            'vm2': 512,
            'vm3': 512}

        assert packing.best_fit_decreasing(
            1, hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {
                'vm1': 'host3',
                'vm2': 'host2',
                'vm3': 'host1'}

        hosts_cpu = {
            'host1': 3000,
            'host2': 1000,
            'host3': 2000}
        hosts_ram = {
            'host1': 4096,
            'host2': 1024,
            'host3': 2048}
        inactive_hosts_cpu = {}
        inactive_hosts_ram = {}
        vms_cpu = {
            'vm1': [100, 1000],
            'vm2': [100, 1000],
            'vm3': [100, 1000]}
        vms_ram = {
            'vm1': 1536,
            'vm2': 512,
            'vm3': 1536}

        assert packing.best_fit_decreasing(
            1, hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {
                'vm1': 'host1',
                'vm2': 'host2',
                'vm3': 'host3'}

        hosts_cpu = {
            'host1': 3000,
            'host2': 1000,
            'host3': 2000}
        hosts_ram = {
            'host1': 4096,
            'host2': 1024,
            'host3': 2048}
        inactive_hosts_cpu = {}
        inactive_hosts_ram = {}
        vms_cpu = {
            'vm1': [100, 1000],
            'vm2': [100, 1000],
            'vm3': [100, 1000]}
        vms_ram = {
            'vm1': 1536,
            'vm2': 1536,
            'vm3': 1536}

        assert packing.best_fit_decreasing(
            1, hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {
                'vm1': 'host1',
                'vm2': 'host1',
                'vm3': 'host3'}

        hosts_cpu = {
            'host1': 3000,
            'host2': 1000,
            'host3': 2000}
        hosts_ram = {
            'host1': 4096,
            'host2': 1024,
            'host3': 2048}
        inactive_hosts_cpu = {}
        inactive_hosts_ram = {}
        vms_cpu = {
            'vm1': [100, 1000],
            'vm2': [100, 1000],
            'vm3': [100, 1000]}
        vms_ram = {
            'vm1': 3072,
            'vm2': 1536,
            'vm3': 1536}

        assert packing.best_fit_decreasing(
            1, hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {}

        hosts_cpu = {
            'host1': 3000,
            'host2': 1000,
            'host3': 2000}
        hosts_ram = {
            'host1': 4096,
            'host2': 1024,
            'host3': 2048}
        inactive_hosts_cpu = {
            'host4': 3000,
            'host5': 1000,
            'host6': 2000}
        inactive_hosts_ram = {
            'host4': 4096,
            'host5': 1024,
            'host6': 2048}
        vms_cpu = {
            'vm1': [100, 1000],
            'vm2': [100, 1000],
            'vm3': [100, 1000]}
        vms_ram = {
            'vm1': 2048,
            'vm2': 4096,
            'vm3': 2048}

        assert packing.best_fit_decreasing(
            1, hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {
                'vm1': 'host6',
                'vm2': 'host1',
                'vm3': 'host3'}

        hosts_cpu = {
            'host1': 3000,
            'host2': 1000,
            'host3': 2000}
        hosts_ram = {
            'host1': 4096,
            'host2': 1024,
            'host3': 2048}
        inactive_hosts_cpu = {
            'host4': 3000,
            'host5': 1000,
            'host6': 2000}
        inactive_hosts_ram = {
            'host4': 4096,
            'host5': 1024,
            'host6': 2048}
        vms_cpu = {
            'vm1': [100, 1000],
            'vm2': [100, 1000],
            'vm3': [100, 1000]}
        vms_ram = {
            'vm1': 2048,
            'vm2': 5120,
            'vm3': 2048}

        assert packing.best_fit_decreasing(
            1, hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {}

        hosts_cpu = {
            'host1': 3000,
            'host2': 1000,
            'host3': 2000}
        hosts_ram = {
            'host1': 4096,
            'host2': 1024,
            'host3': 2048}
        inactive_hosts_cpu = {}
        inactive_hosts_ram = {}
        vms_cpu = {
            'vm1': [1000, 1000],
            'vm2': [0, 2000],
            'vm3': [500, 1500]}
        vms_ram = {
            'vm1': 1536,
            'vm2': 1536,
            'vm3': 1536}

        assert packing.best_fit_decreasing(
            2, hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {
                'vm1': 'host1',
                'vm2': 'host1',
                'vm3': 'host3'}
