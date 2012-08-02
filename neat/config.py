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

"""Configuration reading functions

"""

import os
import ConfigParser


#DEFAILT_CONFIG_PATH = "/etc/neat/neat.conf"
DEFAILT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'neat.conf')

#CONFIG_PATH = "/etc/neat/neat.conf"
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'neat.conf')


def readConfig():
    """Read the configuration files and return a dict
    """
    configParser = ConfigParser.ConfigParser()
    configParser.readfp(open(DEFAILT_CONFIG_PATH))
    configParser.read(CONFIG_PATH)
    return dict(configParser.items("DEFAULT"))
