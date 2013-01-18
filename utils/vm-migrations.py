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

import sys
import os
import random
import shutil
import time
from datetime import datetime
from db import init_db

if len(sys.argv) < 5:
    print 'You must specify 4 arguments:'
    print '1. The MySQL DB user name'
    print '2. The MySQL DB password'
    print '3. The start datetime in the format: %Y-%m-%d %H:%M:%S'
    print '4. The finish datetime in the format: %Y-%m-%d %H:%M:%S'
    sys.exit(1)

db = init_db('mysql://' + sys.argv[1] + ':' + sys.argv[2] + '@localhost/spe')
start_time = datetime.fromtimestamp(
    time.mktime(time.strptime(sys.argv[3], '%Y-%m-%d %H:%M:%S')))
finish_time = datetime.fromtimestamp(
    time.mktime(time.strptime(sys.argv[4], '%Y-%m-%d %H:%M:%S')))

#print "Start time: " + str(start_time)
#print "Finish time: " + str(finish_time)
print "VM migrations: " + str(len(db.select_vm_migrations(start_time, finish_time)))
