#!/usr/bin/python2

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

from novaclient.v1_1 import client
import neat.common as common
from neat.config import *


def vm_hostname(vm):
    return str(getattr(vm, 'OS-EXT-SRV-ATTR:host'))


config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                  REQUIRED_FIELDS)
hosts = common.parse_compute_hosts(config['compute_hosts'])
nova = client.Client(config['os_admin_user'],
                     config['os_admin_password'],
                     config['os_admin_tenant_name'],
                     config['os_auth_url'],
                     service_type="compute")



placement = dict((str(vm.human_id), vm_hostname(vm)) for vm in nova.servers.list())

for vm in sorted(placement.keys()):
    print '{0:15} ==> {1}'.format(vm, placement[vm])
