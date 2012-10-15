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

import neat.globals.db_cleaner as cleaner
import neat.common as common
import neat.db_utils as db_utils

import logging
logging.disable(logging.CRITICAL)


class DbCleaner(TestCase):

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
                'db_cleaner_interval': str(time_interval)}
            paths = [cleaner.DEFAILT_CONFIG_PATH, cleaner.CONFIG_PATH]
            fields = cleaner.REQUIRED_FIELDS
            expect(cleaner).read_and_validate_config(paths, fields). \
                and_return(config).once()
            expect(common).init_logging('dir', 'db-cleaner.log', 2).once()
            expect(common).start(cleaner.init_state,
                                 cleaner.execute,
                                 config,
                                 time_interval).and_return(state).once()
            assert cleaner.start() == state

    @qc(1)
    def init_state():
        with MockTransaction:
            db = mock('db')
            expect(cleaner).init_db('db'). \
                and_return(db).once()
            config = {'sql_connection': 'db',
                      'db_cleaner_interval': 7200}
            state = cleaner.init_state(config)
            assert state['db'] == db
            assert state['time_delta'] == datetime.timedelta(0, 7200)

    @qc(1)
    def execute(
        uuid=str_(of='abc123-', min_length=36, max_length=36)
    ):
        with MockTransaction:
            db = db_utils.init_db('sqlite:///:memory:')
            result = db.vms.insert().execute(uuid=uuid)
            vm_id = result.inserted_primary_key[0]
            time = datetime.datetime.today()
            for i in range(10):
                db.vm_resource_usage.insert().execute(
                    vm_id=1,
                    cpu_mhz=i,
                    timestamp=time.replace(second=i))
            state = {
                'db': db,
                'time_delta': datetime.timedelta(seconds=5)}
            expect(cleaner).today(). \
                and_return(time.replace(second=10)).once()
            assert db.select_cpu_mhz_for_vm(uuid, 100) == range(10)
            cleaner.execute({}, state)
            assert db.select_cpu_mhz_for_vm(uuid, 100) == range(5, 10)
                
