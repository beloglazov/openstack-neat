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

    @contract(connection=Connection, vms=Table, vm_resource_usage=Table)
    def __init__(self, connection, vms, vm_resource_usage):
        """ Initialize the database.

        :param connection: A database connection table.
        :param vms: The vms table.
        :param vm_resource_usage: The vm_resource_usage table.
        """
        self.connection = connection
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
            order_by(self.vm_resource_usage.c.id.desc()). \
            limit(n)
        res = self.connection.execute(sel).fetchall()
        return [x[0] for x in res]
