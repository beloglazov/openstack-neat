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


class BinPacking(TestCase):

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
            'vm1': 2000,
            'vm2': 1000,
            'vm3': 3000}
        vms_ram = {
            'vm1': 512,
            'vm2': 512,
            'vm3': 512}

        assert packing.best_fit_decreasing(
            hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
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
            'vm1': 1000,
            'vm2': 1000,
            'vm3': 1000}
        vms_ram = {
            'vm1': 1536,
            'vm2': 512,
            'vm3': 1536}

        assert packing.best_fit_decreasing(
            hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
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
            'vm1': 1000,
            'vm2': 1000,
            'vm3': 1000}
        vms_ram = {
            'vm1': 1536,
            'vm2': 1536,
            'vm3': 1536}

        assert packing.best_fit_decreasing(
            hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
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
        inactive_hosts_cpu = {
            'host4': 3000,
            'host5': 1000,
            'host6': 2000}
        inactive_hosts_ram = {
            'host4': 4096,
            'host5': 1024,
            'host6': 2048}
        vms_cpu = {
            'vm1': 1000,
            'vm2': 1000,
            'vm3': 1000}
        vms_ram = {
            'vm1': 2048,
            'vm2': 4096,
            'vm3': 2048}

        assert packing.best_fit_decreasing(
            hosts_cpu, hosts_ram, inactive_hosts_cpu, inactive_hosts_ram,
            vms_cpu, vms_ram) == {
            'vm1': 'host6',
            'vm2': 'host1',
            'vm3': 'host3'}


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
