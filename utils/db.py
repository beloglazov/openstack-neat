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
import datetime
from sqlalchemy import *
from sqlalchemy.engine.base import Connection


class Database(object):
    """ A class representing the database, where fields are tables.
    """

    @contract(connection=Connection,
              hosts=Table,
              host_resource_usage=Table,
              vms=Table,
              vm_resource_usage=Table,
              vm_migrations=Table,
              host_states=Table,
              host_overload=Table)
    def __init__(self, connection, hosts, host_resource_usage, vms, 
                 vm_resource_usage, vm_migrations, host_states, host_overload):
        """ Initialize the database.

        :param connection: A database connection table.
        :param hosts: The hosts table.
        :param host_resource_usage: The host_resource_usage table.
        :param vms: The vms table.
        :param vm_resource_usage: The vm_resource_usage table.
        :param vm_migrations: The vm_migrations table.
        :param host_states: The host_states table.
        :param host_overload: The host_overload table.
        """
        self.connection = connection
        self.hosts = hosts
        self.host_resource_usage = host_resource_usage
        self.vms = vms
        self.vm_resource_usage = vm_resource_usage
        self.vm_migrations = vm_migrations
        self.host_states = host_states
        self.host_overload = host_overload

    @contract
    def select_host_ids(self):
        """ Select the IDs of all the hosts.

        :return: A dict of host names to IDs.
         :rtype: dict(str: int)
        """
        return dict((str(x[1]), int(x[0])) 
                    for x in self.hosts.select().execute().fetchall())

    @contract
    def select_host_states(self, host_id, start_time, end_time):
        """ Select the states of a host.

        :param start_time: The start time to select host states.
         :type start_time: *

        :param end_time: The end time to select host states.
         :type end_time: *

        :return: A list of timestamps and host states.
         :rtype: list(tuple(*, int))
        """
        hs = self.host_states
        sel = select([hs.c.timestamp, hs.c.state]). \
            where(and_(hs.c.host_id == host_id,
                       hs.c.timestamp >= start_time,
                       hs.c.timestamp <= end_time)). \
            order_by(hs.c.id.asc())
        return [(x[0], int(x[1])) 
                for x in self.connection.execute(sel).fetchall()]

    @contract
    def select_host_overload(self, host_id, start_time, end_time):
        """ Select the overload of a host.

        :param start_time: The start time to select host overload.
         :type start_time: *

        :param end_time: The end time to select host states.
         :type end_time: *

        :return: A list of timestamps and overloads.
         :rtype: list(tuple(*, int))
        """
        ho = self.host_overload
        sel = select([ho.c.timestamp, ho.c.overload]). \
            where(and_(ho.c.host_id == host_id,
                       ho.c.timestamp >= start_time,
                       ho.c.timestamp <= end_time)). \
            order_by(ho.c.id.asc())
        return [(x[0], int(x[1])) 
                for x in self.connection.execute(sel).fetchall()]

    @contract
    def select_vm_migrations(self, start_time, end_time):
        """ Select VM migrations.

        :param start_time: The start time to select data.
         :type start_time: *

        :param end_time: The end time to select data.
         :type end_time: *

        :return: A list of timestamps and VM IDs.
         :rtype: list(tuple(*, int))
        """
        vm = self.vm_migrations
        sel = select([vm.c.timestamp, vm.c.vm_id]). \
            where(and_(vm.c.timestamp >= start_time,
                       vm.c.timestamp <= end_time)). \
            order_by(vm.c.id.asc())
        return [(x[0], int(x[1])) 
                for x in self.connection.execute(sel).fetchall()]


@contract
def init_db(sql_connection):
    """ Initialize the database.

    :param sql_connection: A database connection URL.
     :type sql_connection: str

    :return: The initialized database.
     :rtype: *
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

    return db
