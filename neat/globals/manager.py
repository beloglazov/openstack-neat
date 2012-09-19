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
from hashlib import sha1

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
def validate_params(params, config):
    """ Validate the input request parameters.

    :param params: A dictionary of input parameters.
     :type params: dict(str: *)

    :param config: A config dictionary.
     :type config: dict(str: str)

    :return: Whether the parameters are valid.
     :rtype: bool
    """
    if 'username' not in params or 'password' not in params:
        raise_error(401)
        return False
    if 'reason' not in params or \
        params['reason'] == 1 and 'vm_uuids' not in params:
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
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH], REQUIRED_FIELDS)
    bottle.debug(True)
    bottle.app().state = {
        'config': config,
        'state': init_state(config)}
    bottle.run(host=config['global_manager_host'], port=config['global_manager_port'])


@bottle.put('/')
def index():
    raise bottle.HTTPResponse(bottle.app().state + 'unprocessable entity', 422)
    return str('asd' not in bottle.request.forms)


@bottle.route('/', method='ANY')
def error():
    raise bottle.HTTPResponse('Method not allowed: the request has been made' +
                              'with a method other than the only supported PUT',
                              405)


@contract
def init_state(config):
    """ Initialize a dict for storing the state of the global manager.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dictionary containing the initial state of the global managerr.
     :rtype: dict
    """
    return {'previous_time': 0,
            'db': init_db(config.get('sql_connection'))}


@contract
def execute(config, state):
    """ Execute an iteration of the global manager

1. Parse the `vm_uuids` parameter and transform it into a list of
   UUIDs of the VMs to migrate.

2. Call the Nova API to obtain the current placement of VMs on the
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

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    return state
