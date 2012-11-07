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

from contracts import contract
from neat.contracts_extra import *

from sqlalchemy import *
from sqlalchemy.sql import func

from neat.db import Database

import logging
log = logging.getLogger(__name__)


@contract
def init_db(sql_connection):
    """ Initialize the database.

    :param sql_connection: A database connection URL.
     :type sql_connection: str

    :return: The initialized database.
     :rtype: Database
    """
    engine = create_engine(sql_connection)  # 'sqlite:///:memory:'
    metadata = MetaData()
    metadata.bind = engine

    hosts = Table('hosts', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('hostname', String(255), nullable=False),
                  Column('cpu_mhz', Integer, nullable=False),
                  Column('cpu_cores', Integer, nullable=False),
                  Column('ram', Integer, nullable=False))

    host_resource_usage = \
        Table('host_resource_usage', metadata,
              Column('id', Integer, primary_key=True),
              Column('host_id', Integer, ForeignKey('hosts.id'), nullable=False),
              Column('timestamp', DateTime, default=func.now()),
              Column('cpu_mhz', Integer, nullable=False))

    vms = Table('vms', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(36), nullable=False))

    vm_resource_usage = \
        Table('vm_resource_usage', metadata,
              Column('id', Integer, primary_key=True),
              Column('vm_id', Integer, ForeignKey('vms.id'), nullable=False),
              Column('timestamp', DateTime, default=func.now()),
              Column('cpu_mhz', Integer, nullable=False))

    vm_migrations = \
        Table('vm_migrations', metadata,
              Column('id', Integer, primary_key=True),
              Column('vm_id', Integer, ForeignKey('vms.id'), nullable=False),
              Column('host_id', Integer, ForeignKey('hosts.id'), nullable=False),
              Column('timestamp', DateTime, default=func.now()))

    host_states = \
        Table('host_states', metadata,
              Column('id', Integer, primary_key=True),
              Column('host_id', Integer, ForeignKey('hosts.id'), nullable=False),
              Column('timestamp', DateTime, default=func.now()),
              Column('state', Integer, nullable=False))

    host_overload = \
        Table('host_overload', metadata,
              Column('id', Integer, primary_key=True),
              Column('host_id', Integer, ForeignKey('hosts.id'), nullable=False),
              Column('timestamp', DateTime, default=func.now()),
              Column('overload', Integer, nullable=False))

    metadata.create_all()
    connection = engine.connect()
    db = Database(connection, hosts, host_resource_usage, vms,
                  vm_resource_usage, vm_migrations, host_states, host_overload)

    log.debug('Initialized a DB connection to %s', sql_connection)
    return db
