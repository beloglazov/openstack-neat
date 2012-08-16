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

import neat.db
import neat.db_utils as db_utils


class DbUtils(TestCase):

    @qc(1)
    def init_db():
        db = db_utils.init_db('sqlite:///:memory:')
        assert type(db) is neat.db.Database
        assert isinstance(db.vms, Table)
        assert isinstance(db.vm_resource_usage, Table)
        assert db.vms.c.keys() == \
            ['id', 'uuid']
        assert db.vm_resource_usage.c.keys() == \
            ['id', 'vm_id', 'timestamp', 'cpu_mhz']
        assert list(db.vm_resource_usage.foreign_keys)[0].target_fullname \
            == 'vms.id'

    @qc(1)
    def insert_select():
        db = db_utils.init_db('sqlite:///:memory:')
        db.vms.insert().execute(uuid='test')
        assert db.vms.select().execute().first()['uuid'] == 'test'
        db.vm_resource_usage.insert().execute(vm_id=1, cpu_mhz=1000)
        assert db.vm_resource_usage.select().execute().first()['cpu_mhz'] == 1000
