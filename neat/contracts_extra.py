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

from contracts import new_contract


new_contract('long', lambda x: isinstance(x, (int, long)))
new_contract('function', lambda x: hasattr(x, '__call__'))

import collections
new_contract('deque', collections.deque)

import datetime
new_contract('datetime', datetime.datetime)

import libvirt
new_contract('virConnect', libvirt.virConnect)
new_contract('virDomain', libvirt.virDomain)

import sqlalchemy
new_contract('Table', sqlalchemy.Table)

import neat.db
new_contract('Database', neat.db.Database)
