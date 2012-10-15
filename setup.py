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

OpenStack Neat is a project intended to provide an extension to
OpenStack implementing dynamic consolidation of Virtual Machines (VMs)
using live migration. The major objective of dynamic VM consolidation
is to improve the utilization of physical resources and reduce energy
consumption by re-allocating VMs using live migration according to
their real-time resource demand and switching idle hosts to the sleep
mode. Apart from consolidating VMs, the system should be able to react
to increases in the resource demand and deconsolidate VMs when
necessary to avoid performance degradation. In general, the problem of
dynamic VM consolidation includes 4 sub-problems: host underload /
overload detection, VM selection, and VM placement.

This work is conducted within the Cloud Computing and Distributed
Systems (CLOUDS) Laboratory (http://www.cloudbus.org/) at the
University of Melbourne. The problem of dynamic VM consolidation
considering Quality of Service (QoS) constraints has been studied from
the theoretical perspective and algorithms addressing the sub-problems
listed above have been proposed [1], [2]. The algorithms have been
evaluated using CloudSim (http://code.google.com/p/cloudsim/) and
real-world workload traces collected from more than a thousand
PlanetLab VMs hosted on servers located in more than 500 places around
the world.

The aim of the OpenStack Neat project is to provide an extensible
framework for dynamic consolidation of VMs based on the OpenStack
platform. The framework should provide an infrastructure enabling the
interaction of components implementing the decision-making algorithms.
The framework should allow configuration-driven switching of different
implementations of the decision-making algorithms. The implementation
of the framework will include the algorithms proposed in our previous
works [1], [2].

[1] Anton Beloglazov and Rajkumar Buyya, "Optimal Online Deterministic
Algorithms and Adaptive Heuristics for Energy and Performance
Efficient Dynamic Consolidation of Virtual Machines in Cloud Data
Centers", Concurrency and Computation: Practice and Experience (CCPE),
Volume 24, Issue 13, Pages: 1397-1420, John Wiley & Sons, Ltd, New
York, USA, 2012. Download:
http://beloglazov.info/papers/2012-optimal-algorithms-ccpe.pdf

[2] Anton Beloglazov and Rajkumar Buyya, "Managing Overloaded Hosts
for Dynamic Consolidation of Virtual Machines in Cloud Data Centers
Under Quality of Service Constraints", IEEE Transactions on Parallel
and Distributed Systems (TPDS), IEEE CS Press, USA, 2012 (in press,
accepted on August 2, 2012). Download:
http://beloglazov.info/papers/2012-host-overload-detection-tpds.pdf
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
    include_package_data=True,
    license='LICENSE',
    packages=find_packages(),
    test_suite='tests',
    tests_require=['pyqcy', 'mocktest', 'PyContracts'],
    entry_points = {
        'console_scripts': [
            'neat-data-collector = neat.locals.collector:start',
            'neat-local-manager  = neat.locals.manager:start',
            'neat-global-manager = neat.globals.manager:start',
            'neat-db-cleaner     = neat.globals.db_cleaner:start',
            ]
        },
    data_files = [('/etc/init.d', ['init.d/openstack-neat-data-collector',
                                   'init.d/openstack-neat-local-manager',
                                   'init.d/openstack-neat-global-manager',
                                   'init.d/openstack-neat-db-cleaner']),
                  ('/etc/neat', ['neat.conf'])],
)
