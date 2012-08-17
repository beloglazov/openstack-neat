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

from neat.db import Database


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

    vms = Table('vms', metadata,
                Column('id', Integer, primary_key=True),
                Column('uuid', String(36), nullable=False))

    vm_resource_usage = Table('vm_resource_usage', metadata,
                Column('id', Integer, primary_key=True),
                Column('vm_id', Integer, ForeignKey('vms.id'), nullable=False),
                Column('timestamp', DateTime, server_default=text('CURRENT_TIMESTAMP')),
                Column('cpu_mhz', Integer, nullable=False))

    metadata.create_all()
    connection = engine.connect()

    return Database(connection, vms, vm_resource_usage)