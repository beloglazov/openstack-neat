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
                Column('vm_id', Integer),
                Column('timestamp', Time, nullable=False),
                Column('cpu_mhz', Integer, nullable=False))

    metadata.create_all(engine)
    engine.connect()

    return Database(vms, vm_resource_usage)


class Database(object):
    """ A class representing the database, where fields are tables.
    """

    @contract
    def __init__(self, vms, vm_resource_usage):
        """ Initialize the database.

        :param vms: The vms table.
         :type vms: Table

        :param vm_resource_usage: The vm_resource_usage table.
         :type vm_resource_usage: Table
        """
        self._vms = vms
        self._vm_resource_usage = vm_resource_usage
