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

import shutil
import libvirt
from hashlib import sha1

import neat.locals.manager as manager
import neat.common as common
import neat.locals.collector as collector

import logging
logging.disable(logging.CRITICAL)


class LocalManager(TestCase):

    @qc(10)
    def start(
            iterations=int_(min=0, max=10),
            time_interval=int_(min=0)
    ):
        with MockTransaction:
            state = {'property': 'value'}
            config = {
                'log_directory': 'dir',
                'log_level': 2,
                'local_manager_interval': str(time_interval)}
            paths = [manager.DEFAILT_CONFIG_PATH, manager.CONFIG_PATH]
            fields = manager.REQUIRED_FIELDS
            expect(manager).read_and_validate_config(paths, fields). \
                and_return(config).once()
            expect(common).init_logging('dir', 'local-manager.log', 2).once()
            expect(common).start(manager.init_state,
                                 manager.execute,
                                 config,
                                 time_interval).and_return(state).once()
            assert manager.start() == state

    @qc(1)
    def init_state():
        with MockTransaction:
            vir_connection = mock('virConnect')
            db = mock('db')
            mhz = 3000
            expect(libvirt).openReadOnly(None). \
                and_return(vir_connection).once()
            expect(manager).init_db('db'). \
                and_return(db).once()
            expect(common).physical_cpu_mhz_total(vir_connection). \
                and_return(mhz)
            expect(vir_connection).getHostname().and_return('host').once()
            config = {'sql_connection': 'db',
                      'os_admin_user': 'user',
                      'os_admin_password': 'password',
                      'host_cpu_usable_by_vms': 0.75}
            state = manager.init_state(config)
            assert state['previous_time'] == 0
            assert state['vir_connection'] == vir_connection
            assert state['db'] == db
            assert state['physical_cpu_mhz_total'] == mhz * 0.75
            assert state['hostname'] == 'host'
            assert state['hashed_username'] == sha1('user').hexdigest()
            assert state['hashed_password'] == sha1('password').hexdigest()

    @qc(1)
    def get_local_vm_data(
        data=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=1, max=3000),
                         min_length=0, max_length=10),
            min_length=0, max_length=5
        )
    ):
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'resources', 'vms', 'tmp')
        shutil.rmtree(path, True)
        os.mkdir(path)
        collector.write_vm_data_locally(path, data, 10)

        assert manager.get_local_vm_data(path) == data
        shutil.rmtree(path)

    @qc(1)
    def get_local_host_data(
        data=list_(of=int_(min=1, max=3000),
                     min_length=0, max_length=10)
    ):
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'resources', 'host')
        assert manager.get_local_host_data(path) == []

        with open(path, 'w') as f:
            f.write('\n'.join([str(x)
                               for x in data]) + '\n')
        assert manager.get_local_host_data(path) == data
        os.remove(path)

    @qc(10)
    def cleanup_vm_data(
        data=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=1, max=3000),
                         min_length=0, max_length=10),
            min_length=0, max_length=5
        )
    ):
        original_data = dict(data)
        uuids = data.keys()
        if data:
            n = random.randrange(len(data))
            for _ in range(n):
                uuid = random.choice(uuids)
                del data[uuid]
                uuids.remove(uuid)

        assert manager.cleanup_vm_data(original_data, uuids) == data

    @qc(10)
    def get_ram(
        data=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=int_(min=1, max=100),
            min_length=0, max_length=10
        )
    ):
        with MockTransaction:
            def mock_get_max_ram(vir_connection, uuid):
                return data[uuid]

            connection = libvirt.virConnect()
            when(manager).get_max_ram(connection, any_string). \
                then_call(mock_get_max_ram)

            assert manager.get_ram(connection, data.keys()) == data

    @qc(10)
    def get_max_ram(
        uuid=str_(of='abc123-', min_length=36, max_length=36),
        x=int_(min=0)
    ):
        with MockTransaction:
            connection = libvirt.virConnect()
            domain = mock('domain')
            expect(connection).lookupByUUIDString(uuid). \
                and_return(domain).once()
            expect(domain).maxMemory().and_return(x).once()
            assert manager.get_max_ram(connection, uuid) == int(x / 1024)

    @qc(1)
    def get_max_ram_none(
        uuid=str_(of='abc123-', min_length=36, max_length=36)
    ):
        with MockTransaction:
            def raise_libvirt_error():
                raise libvirt.libvirtError(None)                
            connection = libvirt.virConnect()
            expect(connection).lookupByUUIDString(uuid). \
                and_call(lambda _: raise_libvirt_error())
            assert manager.get_max_ram(connection, uuid) is None

    def test_vm_mhz_to_percentage(self):
        self.assertEqual(manager.vm_mhz_to_percentage(
            [[100, 200, 300],
             [300, 100, 300, 200],
             [100, 100, 700]],
            [300, 0, 300],
            3000),
            [0.1, 0.2, 0.2, 0.5])

        self.assertEqual(manager.vm_mhz_to_percentage(
            [[100, 200, 300],
             [100, 300, 200],
             [100, 100, 700]],
            [0, 300],
            3000),
            [0.1, 0.2, 0.5])

        self.assertEqual(manager.vm_mhz_to_percentage(
            [[100, 200, 300],
             [300, 100, 300, 200],
             [100, 100, 700]],
            [300, 0, 300, 0, 300],
            3000),
            [0.1, 0.2, 0.2, 0.5])
