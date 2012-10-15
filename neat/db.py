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

import datetime
from sqlalchemy import *
from sqlalchemy.engine.base import Connection

import logging
log = logging.getLogger(__name__)


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
        log.debug('Instantiated a Database object')

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
            order_by(self.vm_resource_usage.c.id.desc()). \
            limit(n)
        res = self.connection.execute(sel).fetchall()
        return list(reversed([int(x[0]) for x in res]))

    @contract
    def select_last_cpu_mhz_for_vms(self):
        """ Select the last value of CPU MHz for all the VMs.

        :return: A dict of VM UUIDs to the last CPU MHz values.
         :rtype: dict(str: int)
        """
        vru1 = self.vm_resource_usage
        vru2 = self.vm_resource_usage.alias()
        sel = select([vru1.c.vm_id, vru1.c.cpu_mhz], from_obj=[
            vru1.outerjoin(vru2, and_(
                vru1.c.vm_id == vru2.c.vm_id,
                vru1.c.id < vru2.c.id))]). \
             where(vru2.c.id == None)
        vms_cpu_mhz = dict(self.connection.execute(sel).fetchall())
        vms_uuids = dict(self.vms.select().execute().fetchall())

        vms_last_mhz = {}
        for id, uuid in vms_uuids.items():
            if id in vms_cpu_mhz:
                vms_last_mhz[str(uuid)] = int(vms_cpu_mhz[id])
            else:
                vms_last_mhz[str(uuid)] = 0
        return vms_last_mhz

    @contract
    def select_vm_id(self, uuid):
        """ Select the ID of a VM by the VM UUID, or insert a new record.

        :param uuid: The UUID of a VM.
         :type uuid: str[36]

        :return: The ID of the VM.
         :rtype: number
        """
        sel = select([self.vms.c.id]).where(self.vms.c.uuid == uuid)
        row = self.connection.execute(sel).fetchone()
        if row is None:
            id = self.vms.insert().execute(uuid=uuid).inserted_primary_key[0]
            log.info('Created a new DB record for a VM %s, id=%d', uuid, id)
            return id
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
    def update_host(self, hostname, cpu_mhz, cpu_cores, ram):
        """ Insert new or update the corresponding host record.

        :param hostname: A host name.
         :type hostname: str

        :param cpu_mhz: The total CPU frequency of the host in MHz.
         :type cpu_mhz: int,>0

        :param cpu_cores: The number of physical CPU cores.
         :type cpu_cores: int,>0

        :param ram: The total amount of RAM of the host in MB.
         :type ram: int,>0

        :return: The ID of the host.
         :rtype: number
        """
        sel = select([self.hosts.c.id]). \
            where(self.hosts.c.hostname == hostname)
        row = self.connection.execute(sel).fetchone()
        if row is None:
            id = self.hosts.insert().execute(
                hostname=hostname,
                cpu_mhz=cpu_mhz,
                cpu_cores=cpu_cores,
                ram=ram).inserted_primary_key[0]
            log.info('Created a new DB record for a host %s, id=%d',
                     hostname, id)
            return id
        else:
            self.connection.execute(self.hosts.update().
                                    where(self.hosts.c.id == row['id']).
                                    values(cpu_mhz=cpu_mhz,
                                           cpu_cores=cpu_cores,
                                           ram=ram))
            return row['id']

    @contract
    def select_host_characteristics(self):
        """ Select the characteristics of all the hosts.

        :return: Three dicts of hostnames to CPU MHz, cores, and RAM.
         :rtype: tuple(dict(str: int), dict(str: int), dict(str: int))
        """
        hosts_cpu_mhz = {}
        hosts_cpu_cores = {}
        hosts_ram = {}
        for x in self.hosts.select().execute().fetchall():
            hostname = str(x[1])
            hosts_cpu_mhz[hostname] = int(x[2])
            hosts_cpu_cores[hostname] = int(x[3])
            hosts_ram[hostname] = int(x[4])
        return hosts_cpu_mhz, hosts_cpu_cores, hosts_ram

    @contract(datetime_threshold=datetime.datetime)
    def cleanup_vm_resource_usage(self, datetime_threshold):
        """ Delete VM resource usage data older than the threshold.

        :param datetime_threshold: A datetime threshold.
         :type datetime_threshold: datetime.datetime
        """
        self.connection.execute(
            self.vm_resource_usage.delete().where(
                self.vm_resource_usage.c.timestamp < datetime_threshold))

