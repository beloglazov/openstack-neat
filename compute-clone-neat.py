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

import subprocess

from neat.config import *
import neat.common as common

commands = [
    'git clone git@github.com:beloglazov/openstack-neat.git',
    'cd openstack-neat',
    'git pull origin master'
]

commands_merged = ''
for command in commands:
    commands_merged += 'echo $ ' + command + ';'
    commands_merged += command + ';'

config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                  REQUIRED_FIELDS)

compute_hosts = common.parse_compute_hosts(config['compute_hosts'])

for host in compute_hosts:
    print 'Host: ' + host
    print subprocess.Popen(
        'ssh ' + host + ' "' + commands_merged + '"', 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True).communicate()[0]
    
