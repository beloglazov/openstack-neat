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

import datetime

import neat.db_utils as db_utils

import logging
logging.disable(logging.CRITICAL)


class Db(TestCase):

    @qc(1)
    def insert_select():
        db = db_utils.init_db('sqlite:///:memory:')
        db.vms.insert().execute(uuid='test')
        assert db.vms.select().execute().first()['uuid'] == 'test'
        db.vm_resource_usage.insert().execute(vm_id=1, cpu_mhz=1000)
        assert db.vm_resource_usage.select(). \
            execute().first()['cpu_mhz'] == 1000

    @qc(10)
    def select_cpu_mhz_for_vm(
        uuid=str_(of='abc123-', min_length=36, max_length=36),
        cpu_mhz=list_(of=int_(min=0, max=3000), min_length=0, max_length=10),
        n=int_(min=1, max=10)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        result = db.vms.insert().execute(uuid=uuid)
        vm_id = result.inserted_primary_key[0]
        for mhz in cpu_mhz:
            db.vm_resource_usage.insert().execute(
                vm_id=vm_id,
                cpu_mhz=mhz)
        assert db.select_cpu_mhz_for_vm(uuid, n) == cpu_mhz[-n:]

    @qc(10)
    def select_last_cpu_mhz_for_vms(
        vms=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=1, max=3000),
                         min_length=0, max_length=10),
            min_length=0, max_length=3
        )
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        res = {}
        for uuid, data in vms.items():
            for value in data:
                db.insert_vm_cpu_mhz({uuid: value})
            if data:
                res[uuid] = data[-1]
        assert db.select_last_cpu_mhz_for_vms() == res

    @qc(10)
    def select_vm_id(
        uuid1=str_(of='abc123-', min_length=36, max_length=36),
        uuid2=str_(of='abc123-', min_length=36, max_length=36)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        result = db.vms.insert().execute(uuid=uuid1)
        vm_id = result.inserted_primary_key[0]
        assert db.select_vm_id(uuid1) == vm_id
        assert db.select_vm_id(uuid2) == vm_id + 1

    @qc(10)
    def insert_vm_cpu_mhz(
        vms=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=tuple_(int_(min=1, max=3000),
                          list_(of=int_(min=1, max=3000),
                                min_length=0, max_length=10)),
            min_length=0, max_length=5
        )
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        initial_data = []
        data_to_submit = {}
        final_data = {}

        for uuid, data in vms.items():
            vm_id = db.select_vm_id(uuid)
            data_to_submit[uuid] = data[0]
            final_data[uuid] = list(data[1])
            final_data[uuid].append(data[0])
            for cpu_mhz in data[1]:
                initial_data.append({'vm_id': vm_id,
                                     'cpu_mhz': cpu_mhz})
        if initial_data:
            db.vm_resource_usage.insert().execute(initial_data)

        db.insert_vm_cpu_mhz(data_to_submit)

        for uuid, data in final_data.items():
            assert db.select_cpu_mhz_for_vm(uuid, 11) == data

    @qc(1)
    def update_host():
        db = db_utils.init_db('sqlite:///:memory:')
        db.update_host('host1', 3000, 4, 4000)
        hosts = db.hosts.select().execute().fetchall()
        assert len(hosts) == 1
        host = hosts[0]
        assert host['hostname'] == 'host1'
        assert host['cpu_mhz'] == 3000
        assert host['cpu_cores'] == 4
        assert host['ram'] == 4000

        db.update_host('host1', 3500, 8, 8000)
        hosts = db.hosts.select().execute().fetchall()
        assert len(hosts) == 1
        host = hosts[0]
        assert host['hostname'] == 'host1'
        assert host['cpu_mhz'] == 3500
        assert host['cpu_cores'] == 8
        assert host['ram'] == 8000

    @qc(10)
    def select_cpu_mhz_for_host(
        hostname=str_(of='abc123', min_length=5, max_length=10),
        cpu_mhz=list_(of=int_(min=0, max=3000), min_length=0, max_length=10),
        n=int_(min=1, max=10)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        host_id = db.update_host(hostname, 1, 1, 1)
        for mhz in cpu_mhz:
            db.host_resource_usage.insert().execute(
                host_id=host_id,
                cpu_mhz=mhz)
        assert db.select_cpu_mhz_for_host(hostname, n) == cpu_mhz[-n:]

    @qc(10)
    def select_last_cpu_mhz_for_hosts(
        hosts=dict_(
            keys=str_(of='abc123', min_length=5, max_length=10),
            values=list_(of=int_(min=1, max=3000),
                         min_length=0, max_length=10),
            min_length=0, max_length=3
        )
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        res = {}
        for hostname, data in hosts.items():
            db.update_host(hostname, 1, 1, 1)
            for value in data:
                db.insert_host_cpu_mhz(hostname, value)
            if data:
                res[hostname] = data[-1]
            else:
                res[hostname] = 0
        assert db.select_last_cpu_mhz_for_hosts() == res

    @qc(10)
    def insert_host_cpu_mhz(
        hostname=str_(of='abc123', min_length=5, max_length=10),
        cpu_mhz=list_(of=int_(min=0, max=3000), min_length=1, max_length=10)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        db.update_host(hostname, 1, 1, 1)
        for value in cpu_mhz:
            db.insert_host_cpu_mhz(hostname, value)
        assert db.select_cpu_mhz_for_host(hostname, len(cpu_mhz)) == cpu_mhz

    @qc(1)
    def select_host_characteristics():
        db = db_utils.init_db('sqlite:///:memory:')
        assert db.select_host_characteristics() == ({}, {}, {})

        db.update_host('host1', 3000, 4, 4000)
        db.update_host('host2', 3500, 8, 8000)
        assert db.select_host_characteristics() == \
            ({'host1': 3000, 'host2': 3500},
             {'host1': 4,    'host2': 8},
             {'host1': 4000, 'host2': 8000})

    @qc(1)
    def select_host_id():
        db = db_utils.init_db('sqlite:///:memory:')
        host1_id = db.hosts.insert().execute(
            hostname='host1',
            cpu_mhz=1,
            cpu_cores=1,
            ram=1).inserted_primary_key[0]
        host2_id = db.hosts.insert().execute(
            hostname='host2',
            cpu_mhz=1,
            cpu_cores=1,
            ram=1).inserted_primary_key[0]
        assert db.select_host_id('host1') == host1_id
        assert db.select_host_id('host2') == host2_id

    @qc(1)
    def select_host_ids():
        db = db_utils.init_db('sqlite:///:memory:')
        assert db.select_host_ids() == {}
        hosts = {}
        hosts['host1'] = db.update_host('host1', 1, 1, 1)
        hosts['host2'] = db.update_host('host2', 1, 1, 1)
        assert db.select_host_ids() == hosts

    @qc(1)
    def cleanup_vm_resource_usage(
        uuid=str_(of='abc123-', min_length=36, max_length=36)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        result = db.vms.insert().execute(uuid=uuid)
        vm_id = result.inserted_primary_key[0]
        time = datetime.datetime.today()
        for i in range(10):
            db.vm_resource_usage.insert().execute(
                vm_id=1,
                cpu_mhz=i,
                timestamp=time.replace(second=i))
        assert db.select_cpu_mhz_for_vm(uuid, 100) == range(10)
        db.cleanup_vm_resource_usage(time.replace(second=5))
        assert db.select_cpu_mhz_for_vm(uuid, 100) == range(5, 10)

    @qc(1)
    def cleanup_host_resource_usage(
        hostname=str_(of='abc123', min_length=5, max_length=10)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        host_id = db.update_host(hostname, 1, 1, 1)
        time = datetime.datetime.today()
        for i in range(10):
            db.host_resource_usage.insert().execute(
                host_id=1,
                cpu_mhz=i,
                timestamp=time.replace(second=i))
        assert db.select_cpu_mhz_for_host(hostname, 100) == range(10)
        db.cleanup_host_resource_usage(time.replace(second=5))
        assert db.select_cpu_mhz_for_host(hostname, 100) == range(5, 10)

    def test_insert_host_states(self):
        db = db_utils.init_db('sqlite:///:memory:')
        hosts = {}
        hosts['host1'] = db.update_host('host1', 1, 1, 1)
        hosts['host2'] = db.update_host('host2', 1, 1, 1)
        db.insert_host_states({'host1': 0, 'host2': 1})
        db.insert_host_states({'host1': 0, 'host2': 0})
        db.insert_host_states({'host1': 1, 'host2': 1})
        result = db.host_states.select().execute().fetchall()
        host1 = [x[3] for x in sorted(filter(
                    lambda x: x[1] == hosts['host1'],
                    result), key=lambda x: x[0])]
        self.assertEqual(host1, [0, 0, 1])
        host2 = [x[3] for x in sorted(filter(
                    lambda x: x[1] == hosts['host2'],
                    result), key=lambda x: x[0])]
        self.assertEqual(host2, [1, 0, 1])

    @qc(10)
    def select_host_states(
        hosts=dict_(
            keys=str_(of='abc123', min_length=1, max_length=5),
            values=list_(of=int_(min=0, max=1),
                         min_length=0, max_length=10),
            min_length=0, max_length=3
        )
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        res = {}
        for host, data in hosts.items():
            db.update_host(host, 1, 1, 1)
            for state in data:
                db.insert_host_states({host: state})
            if data:
                res[host] = data[-1]
            else:
                res[host] = 1
        assert db.select_host_states() == res

    @qc(10)
    def select_active_hosts(
        hosts=dict_(
            keys=str_(of='abc123', min_length=1, max_length=5),
            values=list_(of=int_(min=0, max=1),
                         min_length=0, max_length=10),
            min_length=0, max_length=3
        )
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        res = []
        for host, data in hosts.items():
            db.update_host(host, 1, 1, 1)
            for state in data:
                db.insert_host_states({host: state})
            if data and data[-1] == 1 or not data:
                res.append(host)
        assert set(db.select_active_hosts()) == set(res)

    @qc(10)
    def select_inactive_hosts(
        hosts=dict_(
            keys=str_(of='abc123', min_length=1, max_length=5),
            values=list_(of=int_(min=0, max=1),
                         min_length=0, max_length=10),
            min_length=0, max_length=3
        )
    ):
        hosts = {'1ab': [0], '3222': [0, 0, 1, 1, 1, 1, 0, 0], 'b222b': [0, 0, 1, 1, 1, 0, 1]}
        db = db_utils.init_db('sqlite:///:memory:')
        res = []
        for host, data in hosts.items():
            db.update_host(host, 1, 1, 1)
            for state in data:
                db.insert_host_states({host: state})
            if data and data[-1] == 0:
                res.append(host)
        assert set(db.select_inactive_hosts()) == set(res)

    def test_insert_host_overload(self):
        db = db_utils.init_db('sqlite:///:memory:')
        hosts = {}
        hosts['host1'] = db.update_host('host1', 1, 1, 1)
        hosts['host2'] = db.update_host('host2', 1, 1, 1)
        db.insert_host_overload('host2', False)
        db.insert_host_overload('host1', True)
        db.insert_host_overload('host1', False)
        db.insert_host_overload('host2', True)
        result = db.host_overload.select().execute().fetchall()
        host1 = [x[3] for x in sorted(filter(
                    lambda x: x[1] == hosts['host1'],
                    result), key=lambda x: x[0])]
        self.assertEqual(host1, [1, 0])
        host2 = [x[3] for x in sorted(filter(
                    lambda x: x[1] == hosts['host2'],
                    result), key=lambda x: x[0])]
        self.assertEqual(host2, [0, 1])

    @qc(1)
    def insert_select():
        db = db_utils.init_db('sqlite:///:memory:')
        db.vms.insert().execute(uuid='x' * 36).inserted_primary_key[0]
        vm_id = db.vms.insert().execute(uuid='vm' * 18).inserted_primary_key[0]
        host_id = db.update_host('host', 1, 1, 1)
        db.insert_vm_migration('vm' * 18, 'host')
        result = db.vm_migrations.select().execute().first()
        assert result[1] == vm_id
        assert result[2] == host_id
