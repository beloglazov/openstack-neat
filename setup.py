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

"""
The OpenStack Neat Project
==========================
"""

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages


setup(
    name='openstack-neat',
    version='0.1',
    description='The OpenStack Neat Project',
    long_description=__doc__,
    author='Anton Beloglazov',
    author_email='anton.beloglazov@gmail.com',
    url='https://github.com/beloglazov/openstack-neat',
    platforms='any',

    packages=find_packages(),
    test_suite='tests',
    tests_require=['pyqcy', 'mocktest', 'PyContracts'],
)
