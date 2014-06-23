# OpenStack Neat: A Framework for Dynamic Consolidation of Virtual Machines in Openstack Clouds

OpenStack Neat is an extension to OpenStack implementing dynamic consolidation
of Virtual Machines (VMs) using live migration. The major objective of dynamic
VM consolidation is to improve the utilization of physical resources and reduce
energy consumption by re-allocating VMs using live migration according to their
real-time resource demand and switching idle hosts to the sleep mode.

For example, assume that two VMs are placed on two different hosts, but the
combined resource capacity required by the VMs to serve the current load can be
provided by just one of the hosts. Then, one of the VMs can be migrated to the
host serving the other VM, and the idle host can be switched to a low power mode
to save energy. When the resource demand of either of the VMs increases, they
get deconsolidated to avoid performance degradation. This process is dynamically
managed by OpenStack Neat.

In general, the problem of dynamic VM consolidation can be split into 4
sub-problems:

- Deciding when a host is considered to be underloaded, so that all the VMs
  should be migrated from it, and the host should be switched to a low power
  mode, such as the sleep mode.
- Deciding when a host is considered to be overloaded, so that some VMs should
  be migrated from the host to other hosts to avoid performance degradation.
- Selecting VMs to migrate from an overloaded host out of the full set of the
  VMs currently served by the host.
- Placing VMs selected for migration to other active or re-activated hosts.

The aim of the OpenStack Neat project is to provide an extensible framework for
dynamic consolidation of VMs based on the OpenStack platform. The framework
provides an infrastructure enabling the interaction of components implementing
the 4 decision-making algorithms listed above. The framework allows
configuration-driven switching of different implementations of the
decision-making algorithms. The implementation of the framework includes the
algorithms proposed in our publications [1], [2].


## More details

For more information please refer to the
[paper](http://beloglazov.info/papers/2014-ccpe-openstack-neat.pdf) describing
the architecture and implementation of OpenStack Neat and Chapter 6 of Anton
Beloglazov's PhD thesis: http://beloglazov.info/thesis.pdf


## Installation

Unfortunately, there is no clear installation and usage guide yet. However, the
basic installation steps are the following:

1. Clone the repository on every compute and controller node.
2. Adjust the configuration by modifying neat.conf file in the repo directory on
   every node.
3. Install the package by running the following command from the repo directory
   on every node: `sudo python setup.py install`
4. Start the services by running the following command on the controller: `sudo
   ./all-start.sh`

You can monitor the current VM placement using the `./vm-placement.py` script.

Some information about running experiments on the system can be found in the
following thread:
https://groups.google.com/forum/#!topic/openstack-neat/PKz2vpKPMcA


## Who we are

This work is conducted within the Cloud Computing and Distributed Systems
(CLOUDS) Laboratory at the University of Melbourne: http://www.cloudbus.org/

The problem of dynamic VM consolidation considering Quality of Service (QoS)
constraints has been studied from the theoretical perspective and algorithms
addressing the sub-problems listed above have been proposed [1], [2]. The
algorithms have been evaluated using CloudSim and real-world workload traces
collected from more than a thousand PlanetLab VMs hosted on servers located in
more than 500 places around the world.


## Discussion group / mailing list

Please feel free to post any questions or suggestions in the project's
discussion group: http://groups.google.com/group/openstack-neat


## Issues / bugs

Please submit any bugs you encounter or suggestions for improvements to our
issue tracker: http://github.com/beloglazov/openstack-neat/issues


## Publications

[1] Anton Beloglazov and Rajkumar Buyya, "OpenStack Neat: A Framework for
Dynamic and Energy-Efficient Consolidation of Virtual Machines in OpenStack
Clouds", Concurrency and Computation: Practice and Experience (CCPE), John Wiley
& Sons, Ltd, USA, 2014 (in press, accepted on 19/05/2014).

Download: http://beloglazov.info/papers/2014-ccpe-openstack-neat.pdf

[2] Anton Beloglazov, "Energy-Efficient Management of Virtual Machines in
Data Centers for Cloud Computing", PhD Thesis, The University of Melbourne,
2013.

Download: http://beloglazov.info/thesis.pdf

[3] Anton Beloglazov and Rajkumar Buyya, "Managing Overloaded Hosts for
Dynamic Consolidation of Virtual Machines in Cloud Data Centers Under Quality of
Service Constraints", IEEE Transactions on Parallel and Distributed Systems
(TPDS), Volume 24, Issue 7, Pages 1366-1379, IEEE CS Press, USA, 2013.

Download: http://beloglazov.info/papers/2013-tpds-managing-overloaded-hosts.pdf

[4] Anton Beloglazov and Rajkumar Buyya, "Optimal Online Deterministic
Algorithms and Adaptive Heuristics for Energy and Performance Efficient Dynamic
Consolidation of Virtual Machines in Cloud Data Centers", Concurrency and
Computation: Practice and Experience (CCPE), Volume 24, Issue 13, Pages:
1397-1420, John Wiley & Sons, Ltd, New York, USA, 2012.

Download: http://beloglazov.info/papers/2012-ccpe-vm-consolidation-algorithms.pdf


## License

The source code is distributed under the Apache 2.0 license.

Copyright (C) 2012-2014 Anton Beloglazov.
