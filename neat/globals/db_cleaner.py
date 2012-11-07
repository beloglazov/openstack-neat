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

""" The database cleaner module.

The database cleaner periodically cleans up the data on resource usage
by VMs stored in the database. This is requried to avoid excess growth
of the database size.
"""

from contracts import contract
from neat.contracts_extra import *

import datetime

import neat.common as common
from neat.config import *
from neat.db_utils import *

import logging
log = logging.getLogger(__name__)


@contract
def start():
    """ Start the database cleaner loop.

    :return: The final state.
     :rtype: dict(str: *)
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                      REQUIRED_FIELDS)

    common.init_logging(
        config['log_directory'],
        'db-cleaner.log',
        int(config['log_level']))

    interval = config['db_cleaner_interval']
    if log.isEnabledFor(logging.INFO):
        log.info('Starting the database cleaner, ' +
                 'iterations every %s seconds', interval)
    return common.start(
        init_state,
        execute,
        config,
        int(interval))


@contract
def init_state(config):
    """ Initialize a dict for storing the state of the database cleaner.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dictionary containing the initial state of the database cleaner.
     :rtype: dict
    """
    return {
        'db': init_db(config['sql_connection']),
        'time_delta': datetime.timedelta(
            seconds=int(config['db_cleaner_interval']))}


@contract
def execute(config, state):
    """ Execute an iteration of the database cleaner.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param state: A state dictionary.
     :type state: dict(str: *)

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    datetime_threshold = today() - state['time_delta']
    state['db'].cleanup_vm_resource_usage(datetime_threshold)
    state['db'].cleanup_host_resource_usage(datetime_threshold)
    if log.isEnabledFor(logging.INFO):
        log.info('Cleaned up data older than %s',
                 datetime_threshold.strftime('%Y-%m-%d %H:%M:%S'))
    return state


@contract
def today():
    """ Return the today's datetime.

    :return: A datetime object representing current date and time.
     :rtype: datetime
    """
    return datetime.datetime.today()
