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

""" The main global manager module.

The global manager is deployed on the management host and is
responsible for making VM placement decisions and initiating VM
migrations. It exposes a REST web service, which accepts requests from
local managers. The global manager processes only one type of requests
-- reallocation of a set of VM instances. Once a request is received,
the global manager invokes a VM placement algorithm to determine
destination hosts to migrate the VMs to. Once a VM placement is
determined, the global manager submits a request to the Nova API to
migrate the VMs. The global manager is also responsible for switching
idle hosts to the sleep mode, as well as re-activating hosts when
necessary.

The global manager is agnostic of a particular implementation of the
VM placement algorithm in use. The VM placement algorithm to use can
be specified in the configuration file using the
`algorithm_vm_placement_factory` option. A VM placement algorithm can
call the Nova API to obtain the information about host characteristics
and current VM placement. If necessary, it can also query the central
database to obtain the historical information about the resource usage
by the VMs.

The global manager component provides a REST web service implemented
using the Bottle framework. The authentication is done using the admin
credentials specified in the configuration file. Upon receiving a
request from a local manager, the following steps will be performed:

1. Parse the `vm_uuids` parameter and transform it into a list of
   UUIDs of the VMs to migrate.

2. Call the Nova API to obtain the current placement of VMs on the
   hosts.

3. Call the function specified in the `algorithm_vm_placement_factory`
   configuration option and pass the UUIDs of the VMs to migrate and
   the current VM placement as arguments.

4. Call the Nova API to migrate the VMs according to the placement
   determined by the `algorithm_vm_placement_factory` algorithm.

When a host needs to be switched to the sleep mode, the global manager
will use the account credentials from the `compute_user` and
`compute_password` configuration options to open an SSH connection
with the target host and then invoke the command specified in the
`sleep_command`, which defaults to `pm-suspend`.

When a host needs to be re-activated from the sleep mode, the global
manager will leverage the Wake-on-LAN technology and send a magic
packet to the target host using the `ether-wake` program and passing
the corresponding MAC address as an argument. The mapping between the
IP addresses of the hosts and their MAC addresses is initialized in
the beginning of the global manager's execution.
"""

from contracts import contract
from neat.contracts_extra import *

import bottle
import re
from hashlib import sha1
from novaclient.v1_1 import client

from neat.config import *
from neat.db_utils import *


ERRORS = {
    400: 'Bad input parameter: incorrect or missing parameters',
    401: 'Unauthorized: user credentials are missing',
    403: 'Forbidden: user credentials do not much the ones ' +
         'specified in the configuration file',
    405: 'Method not allowed: the request is made with ' +
         'a method other than the only supported PUT',
    422: 'Unprocessable entity: one or more VMs could not ' +
         'be found using the list of UUIDs specified in ' +
         'the vm_uuids parameter'}


@contract
def raise_error(status_code):
    """ Raise and HTTPResponse exception with the specified status code.

    :param status_code: An HTTP status code of the error.
     :type status_code: int
    """
    if status_code in ERRORS:
        raise bottle.HTTPResponse(ERRORS[status_code], status_code)
    raise bottle.HTTPResponse('Unknown error', 500)


@contract
def validate_params(config, params):
    """ Validate the input request parameters.

    :param config: A config dictionary.
     :type config: dict(str: str)

    :param params: A dictionary of input parameters.
     :type params: dict(str: *)

    :return: Whether the parameters are valid.
     :rtype: bool
    """
    if 'username' not in params or 'password' not in params:
        raise_error(401)
        return False
    if 'reason' not in params or \
       params['reason'] == 1 and 'vm_uuids' not in params or \
       params['reason'] == 0 and 'host' not in params:
        raise_error(400)
        return False
    if sha1(params['username']).hexdigest() != config['admin_user'] or \
       sha1(params['password']).hexdigest() != config['admin_password']:
        raise_error(403)
        return False
    return True


def start():
    """ Start the global manager web service.
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                      REQUIRED_FIELDS)
    bottle.debug(True)
    bottle.app().state = {
        'config': config,
        'state': init_state(config)}
    bottle.run(host=config['global_manager_host'],
               port=config['global_manager_port'])


@contract
def get_params(request):
    """ Return the request data as a dictionary.

    :param request: A Bottle request object.
     :type request: *

    :return: The request data dictionary.
     :rtype: map(str: str)
    """
    return request.forms


@bottle.put('/')
def service():
    params = get_params(bottle.request)
    state = bottle.app().state
    validate_params(state['config'], params)
    if params['reason'] == 0:
        execute_underload(
            state['config'],
            state['state'],
            params['host'])
    else:
        execute_overload(
            state['config'],
            state['state'],
            params['vm_uuids'])


@bottle.route('/', method='ANY')
def error():
    raise bottle.HTTPResponse(
        'Method not allowed: the request has been made' +
        'with a method other than the only supported PUT',
        405)


@contract
def init_state(config):
    """ Initialize a dict for storing the state of the global manager.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dict containing the initial state of the global managerr.
     :rtype: dict
    """
    return {'previous_time': 0,
            'db': init_db(config.get('sql_connection')),
            'nova': client.Client(config.get('os_admin_user'),
                                  config.get('os_admin_password'),
                                  config.get('os_admin_tenant_name'),
                                  config.get('os_auth_url'),
                                  service_type="compute"),
            'compute_hosts': parse_compute_hosts(config['compute_hosts'])}


@contract
def parse_compute_hosts(compute_hosts):
    """ Transform a coma-separated list of host names into a list.

    :param compute_hosts: A coma-separated list of host names.
     :type compute_hosts: str

    :return: A list of host names.
     :rtype: list(str)
    """
    return filter(None, re.split('\W+', compute_hosts))


@contract
def execute_underload(config, state, host):
    """ Process an underloaded host: migrate all VMs from the host.

1. Call the nova API to obtain the UUIDs of the VMs allocated to the
   host.

3. Call the function specified in the `algorithm_vm_placement_factory`
   configuration option and pass the UUIDs of the VMs to migrate and
   the current VM placement as arguments.

4. Call the Nova API to migrate the VMs according to the placement
   determined by the `algorithm_vm_placement_factory` algorithm.

5. Switch off the host at the end of the VM migration.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param state: A state dictionary.
     :type state: dict(str: *)

    :param state: A host name.
     :type state: str

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    underloaded_host = host
    hosts_cpu_total, hosts_ram_total = db.select_host_characteristics()

    hosts_to_vms = vms_by_hosts(state['nova'], config['compute_hosts'])
    vms_last_cpu = state['db'].select_last_cpu_mhz_for_vms()

    hosts_cpu_usage = {}
    hosts_ram_usage = {}
    for host, vms in hosts_to_vms.items():
        host_cpu_mhz = sum(vms_last_cpu[x] for x in vms)
        if host_cpu_mhz > 0:
            host_cpu_usage[host] = host_cpu_mhz
            host_ram_usage[host] = host_used_ram(state['nova'], host)
        else:
            # Exclude inactive hosts
            del hosts_cpu_total[host]
            del hosts_ram_total[host]

    # Exclude the underloaded host
    del hosts_cpu_usage[underloaded_host]
    del hosts_cpu_total[underloaded_host]
    del hosts_ram_usage[underloaded_host]
    del hosts_ram_total[underloaded_host]

    vms_to_migrate = vms_by_host(state['nova'], underloaded_host)
    vms_cpu = {x: vms_last_cpu[x] for x in vms_to_migrate}
    vms_ram = vms_ram_limit(state['nova'], vms_to_migrate)

    time_step = int(config.get('data_collector_interval'))
    migration_time = calculate_migration_time(
        vm_ram,
        float(config.get('network_migration_bandwidth')))

    if 'vm_placement' not in state:
        vm_placement_params = json.loads(
            config.get('algorithm_vm_placement_params'))
        vm_placement_state = None
        vm_placement = config.get('algorithm_vm_placement_factory')(
            time_step,
            migration_time,
            vm_placement_params)
        state['vm_placement'] = vm_placement
    else:
        vm_placement = state['vm_placement']
        vm_placement_state = state['vm_placement_state']

    placement, vm_placement_state = vm_placement(
        hosts_cpu_usage, hosts_cpu_total,
        hosts_ram_usage, hosts_ram_total,
        {}, {},
        vms_cpu, vms_ram,
        vm_placement_state)
    state['vm_placement_state'] = vm_placement_state

    # TODO: initiate VM migrations according to the obtained placement

    return state


@contract
def flavors_ram(nova):
    """ Get a dict of flavor IDs to the RAM limits.

    :param nova: A Nova client.
     :type nova: *

    :return: A dict of flavor IDs to the RAM limits.
     :rtype: dict(str: int)
    """
    return dict((str(fl.id), fl.ram) for fl in nova.flavors.list())


@contract
def vms_ram_limit(nova, vms):
    """ Get the RAM limit from the flavors of the VMs.

    :param nova: A Nova client.
     :type nova: *

    :param vms: A list of VM UUIDs.
     :type vms: list(str)

    :return: A dict of VM UUIDs to the RAM limits.
     :rtype: dict(str: int)
    """
    flavors_to_ram = flavors_ram(nova)
    return dict((uuid, flavors_to_ram[nova.servers.get(uuid).flavor['id']])
                for uuid in vms)


@contract
def host_used_ram(nova, host):
    """ Get the used RAM of the host using the Nova API.

    :param nova: A Nova client.
     :type nova: *

    :param host: A host name.
     :type host: str

    :return: The used RAM of the host.
     :rtype: int
    """
    return nova.hosts.get(host)[1].memory_mb


@contract
def vms_by_host(nova, host):
    """ Get VMs from the specified host using the Nova API.

    :param nova: A Nova client.
     :type nova: *

    :param host: A host name.
     :type host: str

    :return: A list of VM UUIDs from the specified host.
     :rtype: list(str)
    """
    return [vm.id for vm in nova.servers.list()
            if vm_hostname(vm) == host]


@contract
def vms_by_hosts(nova, hosts):
    """ Get a map of host names to VMs using the Nova API.

    :param nova: A Nova client.
     :type nova: *

    :param hosts: A list of host names.
     :type hosts: list(str)

    :return: A dict of host names to lists of VM UUIDs.
     :rtype: dict(str: list(str))
    """
    result = {host: [] for host in hosts}
    for vm in nova.servers.list():
        result[vm_hostname(vm)].append(vm.id)
    return result


@contract
def vm_hostname(vm):
    """ Get the name of the host where VM is running.

    :param vm: A Nova VM object.
     :type vm: *

    :return: The hostname.
     :rtype: str
    """
    return getattr(vm, 'OS-EXT-SRV-ATTR:host')


@contract
def execute_overload(config, state, vm_uuids):
    """ Execute an iteration of the global manager

1. Call the Nova API to obtain the current placement of VMs on the
   hosts.

3. Call the function specified in the `algorithm_vm_placement_factory`
   configuration option and pass the UUIDs of the VMs to migrate and
   the current VM placement as arguments.

4. Call the Nova API to migrate the VMs according to the placement
   determined by the `algorithm_vm_placement_factory` algorithm.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param state: A state dictionary.
     :type state: dict(str: *)

    :param vm_uuids: A list of VM UUIDs to migrate from the host.
     :type vm_uuids: list(str)

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    underloaded_host = host
    hosts_cpu_total, hosts_ram_total = db.select_host_characteristics()

    hosts_to_vms = vms_by_hosts(state['nova'], config['compute_hosts'])
    vms_last_cpu = state['db'].select_last_cpu_mhz_for_vms()

    hosts_cpu_usage = {}
    hosts_ram_usage = {}
    inactive_hosts_cpu = {}
    inactive_hosts_ram = {}
    for host, vms in hosts_to_vms.items():
        host_cpu_mhz = sum(vms_last_cpu[x] for x in vms)
        if host_cpu_mhz > 0:
            host_cpu_usage[host] = host_cpu_mhz
            host_ram_usage[host] = host_used_ram(state['nova'], host)
        else:
            inactive_hosts_cpu[host] = hosts_cpu_total[host]
            inactive_hosts_ram[host] = hosts_ram_total[host]
            del hosts_cpu_total[host]
            del hosts_ram_total[host]

    #fix
    vms_to_migrate = vms_by_host(state['nova'], underloaded_host)


    time_step = int(config.get('data_collector_interval'))
    migration_time = calculate_migration_time(
        vm_ram,
        float(config.get('network_migration_bandwidth')))

    if 'vm_placement' not in state:
        vm_placement_params = json.loads(
            config.get('algorithm_vm_placement_params'))
        vm_placement_state = None
        vm_placement = config.get('algorithm_vm_placement_factory')(
            time_step,
            migration_time,
            vm_placement_params)
        state['vm_placement'] = vm_placement
    else:
        vm_placement = state['vm_placement']
        vm_placement_state = state['vm_placement_state']

    placement, vm_placement_state = vm_placement(
        hosts_cpu_usage, hosts_cpu_total,
        hosts_ram_usage, hosts_ram_total,
        inactive_hosts_cpu, inactive_hosts_ram,
        vm_placement_state)
    state['vm_placement_state'] = vm_placement_state

    return state
