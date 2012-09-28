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

""" A set of functions for reading configuration options from files.

"""

from contracts import contract
import os
import ConfigParser

import logging
log = logging.getLogger(__name__)


# This is the default config, which should not be modified
DEFAILT_CONFIG_PATH = os.path.join(os.path.dirname(__file__),
                                   '..',
                                   'neat.conf')

# This is the custom config, which may override the defaults
CONFIG_PATH = "/etc/neat/neat.conf"
# The following value is used for testing purposes
#CONFIG_PATH = os.path.join(os.path.dirname(__file__),
#                           '..',
#                           'neat.conf')

# These fields must present in the configuration file
REQUIRED_FIELDS = [
    'log_directory',
    'log_level',
    'sql_connection',
    'os_admin_tenant_name',
    'os_admin_user',
    'os_admin_password',
    'os_auth_url',
    'compute_hosts',
    'global_manager_host',
    'global_manager_port',
    'local_data_directory',
    'local_manager_interval',
    'data_collector_interval',
    'data_collector_data_length',
    'compute_user',
    'compute_password',
    'sleep_command',
    'algorithm_underload_detection_factory',
    'algorithm_underload_detection_parameters',
    'algorithm_overload_detection_factory',
    'algorithm_overload_detection_parameters',
    'algorithm_vm_selection_factory',
    'algorithm_vm_selection_parameters',
    'algorithm_vm_placement_factory',
    'algorithm_vm_placement_parameters',
]


@contract
def read_config(paths):
    """ Read the configuration files and return the options.

    :param paths: A list of required configuration file paths.
     :type paths: list(str)

    :return: A dictionary of the configuration options.
     :rtype: dict(str: str)
    """
    configParser = ConfigParser.ConfigParser()
    for path in paths:
        configParser.read(path)
    return dict(configParser.items("DEFAULT"))


@contract
def validate_config(config, required_fields):
    """ Check that the config contains all the required fields.

    :param config: A config dictionary to check.
     :type config: dict(str: str)

    :param required_fields: A list of required fields.
     :type required_fields: list(str)

    :return: Whether the config is valid.
     :rtype: bool
    """
    for field in required_fields:
        if not field in config:
            return False
    return True


@contract
def read_and_validate_config(paths, required_fields):
    """ Read the configuration files, validate and return the options.

    :param paths: A list of required configuration file paths.
     :type paths: list(str)

    :param required_fields: A list of required fields.
     :type required_fields: list(str)

    :return: A dictionary of the configuration options.
     :rtype: dict(str: str)
    """
    config = read_config(paths)
    if not validate_config(config, required_fields):
        message = 'The config dictionary does not contain ' + \
                  'all the required fields'
        log.critical(message)
        raise KeyError(message)
    return config
