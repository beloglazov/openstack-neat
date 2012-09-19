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

import neat.globals.manager as manager
import bottle


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
