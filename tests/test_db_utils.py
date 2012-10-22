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

import logging
logging.disable(logging.CRITICAL)


class DbUtils(TestCase):

    @qc(1)
    def init_db():
        db = db_utils.init_db('sqlite:///:memory:')
        assert type(db) is neat.db.Database
        assert isinstance(db.hosts, Table)
        assert isinstance(db.vms, Table)
        assert isinstance(db.vm_resource_usage, Table)
        assert isinstance(db.host_states, Table)
        assert db.hosts.c.keys() == \
            ['id', 'hostname', 'cpu_mhz', 'cpu_cores', 'ram']
        assert db.host_resource_usage.c.keys() == \
            ['id', 'host_id', 'timestamp', 'cpu_mhz']
        assert list(db.host_resource_usage.foreign_keys)[0].target_fullname \
            == 'hosts.id'
        assert db.vms.c.keys() == \
            ['id', 'uuid']
        assert db.vm_resource_usage.c.keys() == \
            ['id', 'vm_id', 'timestamp', 'cpu_mhz']
        assert list(db.vm_resource_usage.foreign_keys)[0].target_fullname \
            == 'vms.id'
        assert db.vm_migrations.c.keys() == \
            ['id', 'vm_id', 'host_id', 'timestamp']
        keys = set([list(db.vm_migrations.foreign_keys)[0].target_fullname,
                    list(db.vm_migrations.foreign_keys)[1].target_fullname])
        assert keys == set(['vms.id', 'hosts.id'])
        assert db.host_states.c.keys() == \
            ['id', 'host_id', 'timestamp', 'state']
        assert list(db.host_states.foreign_keys)[0].target_fullname \
            == 'hosts.id'
        assert db.host_overload.c.keys() == \
            ['id', 'host_id', 'timestamp', 'overload']
        assert list(db.host_overload.foreign_keys)[0].target_fullname \
            == 'hosts.id'
