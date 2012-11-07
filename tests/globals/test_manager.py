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

import bottle
from hashlib import sha1
from novaclient.v1_1 import client
import time
import subprocess

import neat.globals.manager as manager
import neat.common as common
import neat.db_utils as db_utils

import logging
logging.disable(logging.CRITICAL)


class GlobalManager(TestCase):

    def test_raise_error(self):
        for error_code in [400, 401, 403, 405, 412]:
            try:
                manager.raise_error(error_code)
            except bottle.HTTPResponse as e:
                assert e.status_code == error_code
            else:
                assert False
        try:
            manager.raise_error(1)
        except bottle.HTTPResponse as e:
            assert e.status_code == 500
        else:
            assert False

    def test_error(self):
        try:
            manager.error()
        except bottle.HTTPResponse as e:
            assert e.status_code == 405
        else:
            assert False

    def test_validate_params(self):
        with MockTransaction:
            expect(manager).raise_error(401).and_return(1).exactly(3).times()
            manager.validate_params('test', 'test', {})
            manager.validate_params('test', 'test', {'username': 'test'})
            manager.validate_params('test', 'test', {'password': 'test'})
            
        with MockTransaction:
            expect(manager).raise_error(403).exactly(2).times()
            manager.validate_params(
                sha1('test').hexdigest(),
                sha1('test2').hexdigest(),
                {'username': sha1('test1').hexdigest(),
                 'password': sha1('test2').hexdigest(),
                 'host': 'test',
                 'reason': 0})
            manager.validate_params(
                sha1('test1').hexdigest(),
                sha1('test').hexdigest(),
                {'username': sha1('test1').hexdigest(),
                 'password': sha1('test2').hexdigest(),
                 'host': 'test',
                 'reason': 0})

            assert manager.validate_params(
                sha1('test1').hexdigest(),
                sha1('test2').hexdigest(),
                {'username': sha1('test1').hexdigest(),
                 'password': sha1('test2').hexdigest(),
                 'time': time.time(),
                 'host': 'test',
                 'reason': 1,
                 'vm_uuids': ['qwe', 'asd']})

            assert manager.validate_params(
                sha1('test1').hexdigest(),
                sha1('test2').hexdigest(),
                {'username': sha1('test1').hexdigest(),
                 'password': sha1('test2').hexdigest(),
                 'time': time.time(),
                 'host': 'test',
                 'reason': 0})

        with MockTransaction:
            expect(manager).raise_error(400).exactly(7).times()
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'time': time.time()})
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'time': time.time(),
                                                     'reason': 1})
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'time': time.time(),
                                                     'reason': 0})
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'time': time.time(),
                                                     'reason': 1,
                                                     'host': 'test'})
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'time': time.time(),
                                                     'reason': 0,
                                                     'vm_uuids': []})
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'reason': 0,
                                                     'vm_uuids': []})
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'reason': 1,
                                                     'vm_uuids': []})

        with MockTransaction:
            expect(manager).raise_error(412).exactly(2).times()
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'time': 1.,
                                                     'reason': 0,
                                                     'host': 'test'})
            manager.validate_params('test', 'test', {'username': 'test',
                                                     'password': 'test',
                                                     'time': time.time() - 6,
                                                     'reason': 0,
                                                     'host': 'test'})
            assert manager.validate_params('test', 'test', 
                                           {'username': 'test',
                                            'password': 'test',
                                            'time': time.time(),
                                            'reason': 0,
                                            'host': 'test'})
            assert manager.validate_params('test', 'test', 
                                           {'username': 'test',
                                            'password': 'test',
                                            'time': time.time() - 4,
                                            'reason': 0,
                                            'host': 'test'})


    def test_start(self):
        with MockTransaction:
            app = mock('app')
            db = mock('db')
            hosts = ['host1', 'host2']
            state = {'property': 'value',
                     'db': db,
                     'compute_hosts': hosts,
                     'host_macs': {}}
            config = {
                'log_directory': 'dir',
                'log_level': 2,
                'global_manager_host': 'localhost',
                'global_manager_port': 8080,
                'ether_wake_interface': 'eth0'}
            paths = [manager.DEFAILT_CONFIG_PATH, manager.CONFIG_PATH]
            fields = manager.REQUIRED_FIELDS
            expect(manager).read_and_validate_config(paths, fields). \
                and_return(config).once()
            expect(common).init_logging('dir', 'global-manager.log', 2).once()
            expect(manager).init_state(config). \
                and_return(state).once()
            expect(manager).switch_hosts_on(db, 'eth0', {}, hosts).once()
            expect(bottle).app().and_return(app).once()
            expect(bottle).run(host='localhost', port=8080).once()
            manager.start()

    def test_init_state(self):
        with MockTransaction:
            db = mock('db')
            nova = mock('nova')
            hosts = ['host1', 'host2']
            config = {'sql_connection': 'db',
                      'os_admin_user': 'user',
                      'os_admin_password': 'password',
                      'os_admin_tenant_name': 'tenant',
                      'os_auth_url': 'url',
                      'compute_hosts': 'host1, host2'}
            expect(manager).init_db('db').and_return(db).once()
            expect(client).Client(
                'user', 'password', 'tenant', 'url',
                service_type='compute'). \
                and_return(nova).once()
            expect(common).parse_compute_hosts('host1, host2'). \
                and_return(hosts).once()
            state = manager.init_state(config)
            assert state['previous_time'] == 0
            assert state['db'] == db
            assert state['nova'] == nova
            assert state['hashed_username'] == sha1('user').hexdigest()
            assert state['hashed_password'] == sha1('password').hexdigest()
            assert state['compute_hosts'] == hosts
            assert state['host_macs'] == {}

    def test_service(self):
        app = mock('app')
        state = {'hashed_username': 'user',
                 'hashed_password': 'password'}
        config = {'global_manager_host': 'localhost',
                  'global_manager_port': 8080}
        app.state = {'state': state,
                     'config': config}

        with MockTransaction:
            params = {'reason': 0,
                      'host': 'host'}
            expect(manager).get_params(Any).and_return(params).once()
            expect(manager).get_remote_addr(Any).and_return('addr').once()
            expect(bottle).app().and_return(app).once()
            expect(manager).validate_params('user', 'password', params). \
                and_return(True).once()
            expect(manager).execute_underload(config, state, 'host').once()
            manager.service()

        with MockTransaction:
            params = {'reason': 1,
                      'host': 'host',
                      'vm_uuids': 'vm_uuids'}
            expect(manager).get_params(Any).and_return(params).once()
            expect(manager).get_remote_addr(Any).and_return('addr').once()
            expect(bottle).app().and_return(app).once()
            expect(manager).validate_params('user', 'password', params). \
                and_return(True).once()
            expect(manager).execute_overload(config, state, 'host', 'vm_uuids'). \
                once()
            manager.service()

    @qc(20)
    def vms_by_host(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=str_(of='abc123-', min_length=10, max_length=10),
            min_length=0, max_length=3
        ),
        y=list_(str_(of='abc123-', min_length=36, max_length=36),
                min_length=0, max_length=3),
        host=str_(of='abc123-', min_length=5, max_length=5)
    ):
        with MockTransaction:
            extra_vms = {}
            for vm in y:
                extra_vms[vm] = host
            x.update(extra_vms)
            vms = []
            for vm_uuid, h in x.items():
                vm = mock(vm_uuid)
                vm.id = vm_uuid
                expect(manager).vm_hostname(vm).and_return(h).once()
                vms.append(vm)
            nova = mock('nova')
            nova.servers = mock('servers')
            expect(nova.servers).list().and_return(vms).once()
            assert set(manager.vms_by_host(nova, host)) == set(y)

    @qc(1)
    def vms_by_hosts(
        x=list_(str_(of='abc123-', min_length=36, max_length=36),
                min_length=0, max_length=3),
        y=list_(str_(of='abc123-', min_length=36, max_length=36),
                min_length=0, max_length=3),
        host1=str_(of='abc123-', min_length=5, max_length=10),
        host2=str_(of='abc123-', min_length=5, max_length=10)
    ):
        with MockTransaction:
            vms1 = {}
            for vm in x:
                vms1[vm] = host1
            vms2 = {}
            for vm in y:
                vms2[vm] = host2
            vms_all = dict(vms1)
            vms_all.update(vms2)
            vms = []
            for vm_uuid, h in vms_all.items():
                vm = mock(vm_uuid)
                vm.id = vm_uuid
                expect(manager).vm_hostname(vm).and_return(h).once()
                vms.append(vm)
            nova = mock('nova')
            nova.servers = mock('servers')
            expect(nova.servers).list().and_return(vms).once()
            result = manager.vms_by_hosts(nova, [host1, host2])
            result_sets = {}
            for host, data in result.items():
                result_sets[host] = set(data)
            assert result_sets == {host1: set(x), host2: set(y)}

    def test_host_used_ram(self):
        with MockTransaction:
            hostname = 'hosthost'
            nova = mock('nova')
            nova.hosts = mock('hosts')
            host1 = mock('host1')
            host1.memory_mb = 4000
            host2 = mock('host2')
            host2.memory_mb = 3000
            expect(nova.hosts).get(hostname). \
                and_return([host1, host2]).once()
            assert manager.host_used_ram(nova, hostname) == 3000

        with MockTransaction:
            hostname = 'hosthost'
            nova = mock('nova')
            nova.hosts = mock('hosts')
            host1 = mock('host1')
            host1.memory_mb = 4000
            host2 = mock('host2')
            host2.memory_mb = 3000
            host3 = mock('host3')
            host3.memory_mb = 3500
            expect(nova.hosts).get(hostname). \
                and_return([host1, host2, host3]).once()
            assert manager.host_used_ram(nova, hostname) == 3500

    def test_flavors_ram(self):
        with MockTransaction:
            nova = mock('nova')
            nova.flavors = mock('flavors')
            fl1 = mock('fl1')
            fl1.id = '1'
            fl1.ram = 1000
            fl2 = mock('fl2')
            fl2.id = '2'
            fl2.ram = 2000
            expect(nova.flavors).list().and_return([fl1, fl2]).once()
            assert manager.flavors_ram(nova) == {'1': 1000, '2': 2000}

    def test_vms_ram_limit(self):
        with MockTransaction:
            nova = mock('nova')
            nova.servers = mock('servers')
            flavors_to_ram = {'1': 512, '2': 1024}
            expect(manager).flavors_ram(nova). \
                and_return(flavors_to_ram).once()

            vm1 = mock('vm1')
            vm1.flavor = {'id': '1'}
            vm2 = mock('vm2')
            vm2.flavor = {'id': '2'}
            expect(nova.servers).get('vm1').and_return(vm1).once()
            expect(nova.servers).get('vm2').and_return(vm2).once()
            assert manager.vms_ram_limit(nova, ['vm1', 'vm2']) == \
                {'vm1': 512, 'vm2': 1024}

    def test_switch_hosts_off(self):
        db = db_utils.init_db('sqlite:///:memory:')          

        with MockTransaction:
            expect(subprocess).call('ssh h1 "sleep"', shell=True).once()
            expect(subprocess).call('ssh h2 "sleep"', shell=True).once()
            expect(db).insert_host_states({
                    'h1': 0,
                    'h2': 0}).once()
            manager.switch_hosts_off(db, 'sleep', ['h1', 'h2'])

        with MockTransaction:
            expect(subprocess).call.never()
            expect(db).insert_host_states({
                    'h1': 0,
                    'h2': 0}).once()
            manager.switch_hosts_off(db, '', ['h1', 'h2'])

    def test_switch_hosts_on(self):
        db = db_utils.init_db('sqlite:///:memory:')          

        with MockTransaction:
            expect(subprocess).call('ether-wake -i eth0 mac1', shell=True).once()
            expect(subprocess).call('ether-wake -i eth0 mac2', shell=True).once()
            expect(manager).host_mac('h1').and_return('mac1').once()
            expect(db).insert_host_states({
                    'h1': 1,
                    'h2': 1}).once()
            manager.switch_hosts_on(db, 'eth0', {'h2': 'mac2'}, ['h1', 'h2'])

        with MockTransaction:
            expect(subprocess).call('ether-wake -i eth0 mac1', shell=True).once()
            expect(subprocess).call('ether-wake -i eth0 mac2', shell=True).once()
            expect(manager).host_mac('h1').and_return('mac1').once()
            expect(manager).host_mac('h2').and_return('mac2').once()
            expect(db).insert_host_states({
                    'h1': 1,
                    'h2': 1}).once()
            manager.switch_hosts_on(db, 'eth0', {}, ['h1', 'h2'])
