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
from sqlalchemy import *
from sqlalchemy.engine.base import Connection


class Database(object):
    """ A class representing the database, where fields are tables.
    """

    @contract(connection=Connection,
              hosts=Table,
              vms=Table,
              vm_resource_usage=Table)
    def __init__(self, connection, hosts, vms, vm_resource_usage):
        """ Initialize the database.

        :param connection: A database connection table.
        :param hosts: The hosts table.
        :param vms: The vms table.
        :param vm_resource_usage: The vm_resource_usage table.
        """
        self.connection = connection
        self.hosts = hosts
        self.vms = vms
        self.vm_resource_usage = vm_resource_usage

    @contract
    def select_cpu_mhz_for_vm(self, uuid, n):
        """ Select n last values of CPU MHz for a VM UUID.

        :param uuid: The UUID of a VM.
         :type uuid: str[36]

        :param n: The number of last values to select.
         :type n: int,>0

        :return: The list of n last CPU Mhz values.
         :rtype: list(int)
        """
        sel = select([self.vm_resource_usage.c.cpu_mhz]). \
            where(and_(
                self.vms.c.id == self.vm_resource_usage.c.vm_id,
                self.vms.c.uuid == uuid)). \
            order_by(self.vm_resource_usage.c.id.asc()). \
            limit(n)
        res = self.connection.execute(sel).fetchall()
        return [x[0] for x in res]

    @contract
    def select_vm_id(self, uuid):
        """ Select the ID of a VM by the VM UUID, or insert a new record.

        :param uuid: The UUID of a VM.
         :type uuid: str[36]

        :return: The ID of the VM.
         :rtype: int
        """
        sel = select([self.vms.c.id]).where(self.vms.c.uuid == uuid)
        row = self.connection.execute(sel).fetchone()
        if row == None:
            return self.vms.insert().execute(uuid=uuid).inserted_primary_key[0]
        else:
            return row['id']

    @contract
    def insert_cpu_mhz(self, data):
        """ Insert a set of CPU MHz values for a set of VMs.

        :param data: A dictionary of VM UUIDs and CPU MHz values.
         :type data: dict(str : int)
        """
        if data:
            query = []
            for uuid, cpu_mhz in data.items():
                vm_id = self.select_vm_id(uuid)
                query.append({'vm_id': vm_id,
                              'cpu_mhz': cpu_mhz})
            self.vm_resource_usage.insert().execute(query)

    @contract
    def update_host(self, hostname, cpu_mhz, ram):
        """ Insert new or update the corresponding host record.

        :param hostname: A host name.
         :type hostname: str

        :param cpu_mhz: The total CPU frequency of the host in MHz.
         :type cpu_mhz: int,>0

        :param ram: The total amount of RAM of the host in MB.
         :type ram: int,>0

        :return: The ID of the host.
         :rtype: int
        """
        sel = select([self.hosts.c.id]).where(self.hosts.c.hostname == hostname)
        row = self.connection.execute(sel).fetchone()
        if row == None:
            return self.hosts.insert().execute(hostname=hostname,
                                               cpu_mhz=cpu_mhz,
                                               ram=ram).inserted_primary_key[0]
        else:
            self.connection.execute(self.hosts.update().
                                    where(self.hosts.c.id == row['id']).
                                    values(cpu_mhz=cpu_mhz,
                                           ram=ram))
            return row['id']
