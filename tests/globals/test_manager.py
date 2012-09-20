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

import neat.globals.manager as manager


class GlobalManager(TestCase):

    def test_raise_error(self):
        for error_code in [400, 401, 403, 405, 422]:
            try:
                manager.raise_error(error_code)
            except bottle.HTTPResponse as e:
                assert e.status == error_code
            else:
                assert False
        try:
            manager.raise_error(1)
        except bottle.HTTPResponse as e:
            assert e.status == 500
        else:
            assert False

    def test_error(self):
        try:
            manager.error()
        except bottle.HTTPResponse as e:
            assert e.status == 405
        else:
            assert False

    def test_validate_params(self):
        with MockTransaction:
            expect(manager).raise_error(401).and_return(1).exactly(3).times()
            manager.validate_params({}, {})
            manager.validate_params({}, {'username': 'test'})
            manager.validate_params({}, {'password': 'test'})

        with MockTransaction:
            expect(manager).raise_error(400).exactly(5).times()
            manager.validate_params({}, {'username': 'test', 'password': 'test'})
            manager.validate_params({}, {'username': 'test',
                                         'password': 'test',
                                         'reason': 1})
            manager.validate_params({}, {'username': 'test',
                                         'password': 'test',
                                         'reason': 0})
            manager.validate_params({}, {'username': 'test',
                                         'password': 'test',
                                         'reason': 1,
                                         'host': 'test'})
            manager.validate_params({}, {'username': 'test',
                                         'password': 'test',
                                         'reason': 0,
                                         'vm_uuids': []})

        with MockTransaction:
            expect(manager).raise_error(403).exactly(2).times()
            manager.validate_params({'admin_user': sha1('test').hexdigest(),
                                     'admin_password': sha1('test2').hexdigest()},
                                    {'username': 'test1',
                                     'password': 'test2',
                                     'reason': 0,
                                     'host': 'test'})
            manager.validate_params({'admin_user': sha1('test1').hexdigest(),
                                     'admin_password': sha1('test').hexdigest()},
                                    {'username': 'test1',
                                     'password': 'test2',
                                     'reason': 0,
                                     'host': 'test'})

            assert manager.validate_params(
                {'admin_user': sha1('test1').hexdigest(),
                 'admin_password': sha1('test2').hexdigest()},
                {'username': 'test1',
                 'password': 'test2',
                 'reason': 1,
                 'vm_uuids': ['qwe', 'asd']}) == True

            assert manager.validate_params(
                {'admin_user': sha1('test1').hexdigest(),
                 'admin_password': sha1('test2').hexdigest()},
                {'username': 'test1',
                 'password': 'test2',
                 'reason': 0,
                 'host': 'test'}) == True

    def test_start(self):
        with MockTransaction:
            app = mock('app')
            state = {'property': 'value'}
            config = {'global_manager_host': 'localhost',
                      'global_manager_port': 8080}
            paths = [manager.DEFAILT_CONFIG_PATH, manager.CONFIG_PATH]
            fields = manager.REQUIRED_FIELDS
            expect(manager).read_and_validate_config(paths, fields). \
              and_return(config).once()
            expect(manager).init_state(config). \
              and_return(state).once()
            expect(bottle).app().and_return(app).once()
            expect(bottle).run(host='localhost', port=8080).once()
            manager.start()

    def test_init_state(self):
        with MockTransaction:
            db = mock('db')
            expect(manager).init_db('db').and_return(db).once()
            config = {'sql_connection': 'db'}
            state = manager.init_state(config)
            assert state['previous_time'] == 0
            assert state['db'] == db

    def test_service(self):
        app = mock('app')
        state = {'property': 'value'}
        config = {'global_manager_host': 'localhost',
                  'global_manager_port': 8080}
        app.state = {'state': state,
                     'config': config}

        with MockTransaction:
            params = {'reason': 0,
                      'host': 'host'}
            expect(manager).get_params(Any).and_return(params).once()
            expect(bottle).app().and_return(app).once()
            expect(manager).validate_params(config, params).and_return(True).once()
            expect(manager).execute_underload(config, state, 'host').once()
            manager.service()

        with MockTransaction:
            params = {'reason': 1,
                      'vm_uuids': 'vm_uuids'}
            expect(manager).get_params(Any).and_return(params).once()
            expect(bottle).app().and_return(app).once()
            expect(manager).validate_params(config, params).and_return(True).once()
            expect(manager).execute_overload(config, state, 'vm_uuids').once()
            manager.service()
