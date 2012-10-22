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
import neat.globals.manager as manager
from neat.config import *
import sys


def vm_hostname(vm):
    return str(getattr(vm, 'OS-EXT-SRV-ATTR:host'))


config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                  REQUIRED_FIELDS)
db = manager.init_db(config['sql_connection'])
nova = client.Client(config['os_admin_user'],
                     config['os_admin_password'],
                     config['os_admin_tenant_name'],
                     config['os_auth_url'],
                     service_type="compute")
hosts = common.parse_compute_hosts(config['compute_hosts'])

hosts_cpu_total, hosts_cpu_cores, hosts_ram_total = \
    db.select_host_characteristics()
hosts_cpu_core = \
    dict((host, int(hosts_cpu_total[host] / hosts_cpu_cores[host]))
         for host in hosts_cpu_total.keys())
hosts_to_vms = manager.vms_by_hosts(nova, hosts)
vms = [item for sublist in hosts_to_vms.values() for item in sublist]

vms_names = []
vms_status = {}
for uuid in vms:
    vm = nova.servers.get(uuid)
    vms_names.append((vm.human_id, uuid))
    vms_status[uuid] = str(vm.status)
vms_names = sorted(vms_names)

vms_cpu_usage = db.select_last_cpu_mhz_for_vms()
for vm in vms:
    if not vm in vms_cpu_usage:
        vms_cpu_usage[vm] = 0
vms_ram_usage = manager.vms_ram_limit(nova, vms)

hosts_cpu_usage_hypervisor = db.select_last_cpu_mhz_for_hosts()

hosts_cpu_usage = {}
hosts_ram_usage = {}
for host, vms in hosts_to_vms.items():
    hosts_cpu_usage[host] = hosts_cpu_usage_hypervisor[host] + \
                            sum(vms_cpu_usage[x] for x in vms)
    hosts_ram_usage[host] = manager.host_used_ram(nova, host)
        

first = True
for host in sorted(hosts_to_vms.keys()):
    if not first:
        print "-----------------------------------------------------------"
    first = False
    vms = hosts_to_vms[host]
    print '{0:24} {1:5d} / {2:5d} MHz {3:5d} / {4:5d} MB'. \
        format(host, 
               hosts_cpu_usage[host], 
               hosts_cpu_total[host],
               hosts_ram_usage[host],
               hosts_ram_total[host])
    for vm, uuid in vms_names:
        if uuid in vms:
            if uuid not in vms_ram_usage:
                vms_ram = 0
            else:
                vms_ram = vms_ram_usage[uuid]
            print '    {0:10} {1:9} {2:5d} / {3:5d} MHz {4:5d} / {5:5d} MB'. \
                format(vm,
                       vms_status[uuid],
                       vms_cpu_usage[uuid], 
                       hosts_cpu_core[host],
                       vms_ram,
                       vms_ram)
