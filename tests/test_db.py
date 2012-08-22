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

from sqlalchemy import *

import neat.db_utils as db_utils


class DbUtils(TestCase):

    @qc(1)
    def insert_select():
        db = db_utils.init_db('sqlite:///:memory:')
        db.vms.insert().execute(uuid='test')
        assert db.vms.select().execute().first()['uuid'] == 'test'
        db.vm_resource_usage.insert().execute(vm_id=1, cpu_mhz=1000)
        assert db.vm_resource_usage.select().execute().first()['cpu_mhz'] == 1000

    @qc(10)
    def select_cpu_mhz_for_vm(
        uuid=str_(of='abc123-', min_length=36, max_length=36),
        cpu_mhz=list_(of=int_(min=0, max=3000), min_length=0, max_length=10),
        n=int_(min=1, max=10)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        result = db.vms.insert().execute(uuid=uuid)
        vm_id = result.inserted_primary_key[0]
        for mhz in reversed(cpu_mhz):
            db.vm_resource_usage.insert().execute(
                vm_id=vm_id,
                cpu_mhz=mhz)
        assert db.select_cpu_mhz_for_vm(uuid, n) == cpu_mhz[:n]

    @qc(10)
    def select_vm_id(
        uuid=str_(of='abc123-', min_length=36, max_length=36)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        result = db.vms.insert().execute(uuid=uuid)
        vm_id = result.inserted_primary_key[0]
        assert db.select_vm_id(uuid) == vm_id

    # @qc(10)
    # def insert_cpu_mhz(
    #     uuid=str_(of='abc123-', min_length=36, max_length=36),
    #     cpu_mhz=list_(of=int_(min=0, max=3000), min_length=0, max_length=10),
    #     n=int_(min=1, max=10)
    # ):
    #     db = db_utils.init_db('sqlite:///:memory:')
    #     result = db.vms.insert().execute(uuid=uuid)
    #     vm_id = result.inserted_primary_key[0]
    #     for mhz in reversed(cpu_mhz):
    #         db.vm_resource_usage.insert().execute(
    #             vm_id=vm_id,
    #             cpu_mhz=mhz)
    #     assert db.select_cpu_mhz_for_vm(uuid, n) == cpu_mhz[:n]
