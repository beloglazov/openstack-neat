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
import neat.common as common


class GlobalManager(TestCase):

    @qc(10)
    def start(
            iterations=int_(min=0, max=10),
            time_interval=int_(min=0)
    ):
        with MockTransaction:
            state = {'property': 'value'}
            config = {'global_manager_interval': time_interval}
            paths = [manager.DEFAILT_CONFIG_PATH, manager.CONFIG_PATH]
            fields = manager.REQUIRED_FIELDS
            expect(manager).read_and_validate_config(paths, fields). \
                and_return(config).once()
            expect(common).start(manager.init_state,
                                 manager.execute,
                                 config,
                                 time_interval).and_return(state).once()
            assert manager.start() == state

    @qc(1)
    def init_state():
        with MockTransaction:
            db = mock('db')
            expect(manager).init_db('db').and_return(db).once()
            config = {'sql_connection': 'db'}
            state = manager.init_state(config)
            assert state['previous_time'] == 0
            assert state['db'] == db
