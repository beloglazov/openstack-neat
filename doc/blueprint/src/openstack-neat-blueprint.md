% OpenStack Neat -- Dynamic Consolidation of Virtual Machines: Blueprint
% Anton Beloglazov
% 26th of July 2012


# Summary

OpenStack Neat is a project intended to provide an extension to OpenStack implementing dynamic
consolidation of Virtual Machines (VMs) using live migration. The major objective of dynamic VM
consolidation is to improve the utilization of physical resources and reduce energy consumption by
re-allocating VMs using live migration according to their real-time resource demand and switching
idle hosts to the sleep mode. For example, assume that two VMs are placed on two different hosts,
but the combined resource capacity required by the VMs to serve the current load can be provided by
just one of the hosts. Then, one of the VMs can be migrated to the host serving the other VM, and
the idle host can be switched to the sleep mode to save energy.

Apart from consolidating VMs, the system should be able to react to increases in the resource demand
and deconsolidate VMs when necessary to avoid performance degradation. In general, the problem of
dynamic VM consolidation can be split into 4 sub-problems:

1. Deciding when a host is considered to be underloaded, so that all the VMs should be migrated out,
and the host should be switched to a low-power mode, such as the sleep mode.
2. Deciding when a host is considered to be overloaded, so that some VMs should be migrated from the
host to other hosts to avoid performance degradation.
3. Selecting VMs, which should be migrated from an overloaded host out of the full set of the VMs
currently served by the host.
4. Placing VMs selected for migration to other active or re-activated hosts.

This work is a part of PhD research conducted within the
[Cloud Computing and Distributed Systems (CLOUDS) Laboratory](http://www.cloudbus.org/) at the
University of Melbourne. The problem of dynamic VM consolidation considering Quality of Service
(QoS) constraints has been studied from the theoretical perspective and algorithms addressing the
sub-problems listed above have been proposed [@beloglazov2012optimal; @beloglazov2012overload]. The
algorithms have been evaluated using [CloudSim](http://code.google.com/p/cloudsim/) and real-world
workload traces collected from more than a thousand [PlanetLab](https://www.planet-lab.org/) VMs
hosted on servers located in more than 500 places around the world.

The aim of the OpenStack Neat project is to provide an extensible framework for dynamic
consolidation of VMs within OpenStack environments. The framework should provide an infrastructure
enabling the interaction of components implementing the 4 decision-making algorithms listed above.
The framework should allow configuration-driven switching of implementations of the decision-making
algorithms. The implementation of the framework will include the algorithms proposed in our previous
works [@beloglazov2012optimal; @beloglazov2012overload].



# Release Note

The functionality covered by this project will be implemented in the form of services separate from
the core OpenStack services. The services of this project will interact with the core OpenStack
services using their public APIs. It will be required to create a new Keystone user within the
`service` tenant. The project will also require a new MySQL database for storing information about
the host configuration, VM placement, and CPU utilization by the VMs. The project will provide a
script for automated initialization of the database. The services provided by the project will need
to be run on the management as well as compute hosts.


# Rationale

The problem of data centers is high energy consumption, which has risen by 56% from 2005 to 2010,
and in 2010 accounted to be between 1.1% and 1.5% of the global electricity use [@koomey2011growth].
Apart from high operating costs, this results in substantial carbon dioxide (CO~2~) emissions, which
are estimated to be 2% of the global emissions [@gartner2007co2]. The problem has been partially
addressed by improvements in the physical infrastructure of modern data centers. As reported by
[the Open Compute Project](http://opencompute.org/), Facebook's Oregon data center achieves a Power
Usage Effectiveness (PUE) of 1.08, which means that approximately 93 of the data center's energy
consumption are consumed by the computing resources. Therefore, now it is important to focus on the
resource management aspect, i.e. ensuring that the computing resources are efficiently utilized to
serve applications.

Dynamic consolidation of VMs has been shown to be efficient in improving the utilization of data
center resources and reducing energy consumption, as demonstrated by numerous studies
[@nathuji2007virtualpower; @verma2008pmapper; @zhu20081000; @gmach2008integrated; @gmach2009resource; @vmware2010distributed; @jung2010mistral; @zheng2009justrunit; @kumar2009vmanage; @guenter2011managing; @bobroff2007dynamic; @beloglazov2011taxonomy].
In this project, we aim to implement an extensible framework for dynamic VM consolidation
specifically targeted at the OpenStack platform.


# User stories

- As a Cloud Administrator or Systems Integrator, I want to support dynamic VM consolidation to
  improve the utilization of the data center's resources and reduce the energy consumption.
- As a Cloud Administrator, I want to provide QoS guarantees to the consumers, while applying
  dynamic VM consolidation.
- As a Cloud Administrator, I want to minimize the price of the service provided to the consumers by
  reducing the operating costs through the reduced energy consumption.
- As a Cloud Administrator, I want to decrease the carbon dioxide emissions into the environment by
  reducing the energy consumption by the data center's resources.
- As a Cloud Service Consumer, I want to pay the minimum price for the service provided through the
  minimized energy consumption of the computing resources.
- As a Cloud Service Consumer, I want to use Green Cloud resources, whose provider strives to reduce
  the impact on the environment in terms of carbon dioxide emissions.


# Assumptions

Nova uses a *shared storage* for storing VM instance data, thus supporting *live migration* of VMs.


# Design

![The deployment diagram](openstack-neat-deployment-diagram.png)

The system is composed of a number of components and data stores, some of which are deployed on the
compute hosts, and some on the management host (Figure 1). In the following sections, we discuss the
design and interaction of the components, as well as the specification of the data stores.


## Components

As shown in Figure 1, the system is composed of three main components:

- *Global manager* -- a component that is deployed on the management host and makes global
   management decisions, such as mapping VM instances on hosts, and initiating VM migrations.
- *Local manager* -- a component that is deployed on every compute host and makes local decisions,
   such as deciding that the host is underloaded or overloaded, and selecting VMs to migrate to
   other hosts.
- *Data collector* -- a component that is deployed on every compute host and is responsible for
   collecting data about resource usage by VM instances, as well as storing these data locally and
   submitting the data to the central database.


### Global Manager

![The global manager: a sequence diagram](openstack-neat-sequence-diagram.png)

The global manager is deployed on the management host and is responsible for making VM placement
decisions and initiating VM migrations. It exposes a REST interface, which accepts requests from
local managers. The global manager processes only one type of requests -- reallocation of a set of
VM instances. As shown in Figure 2, once a request is received, the global manager invokes a VM
placement algorithm to determine destination hosts to migrate the VMs to. Once a VM placement is
determined, the global manager submits a request to the Nova API to migrate the VMs. When the
required VM migrations are completed, the global manager sends an acknowledgment message to the
local managers of both source and destination hosts to update their VM metadata. The global manager
is also responsible for switching idle hosts to the sleep mode, as well as re-activating hosts when
necessary.

The global manager is agnostic of a particular implementation of the VM placement algorithm in use.
The VM placement algorithm to use can be specified in the configuration file described later. A VM
placement algorithm can the Nova API to obtain the information about host characteristics and
current VM placement. If necessary, it can also query the central database to obtain the historical
information about the resource usage by the VMs.


### Local Manager

![The local manager: an activity diagram](openstack-neat-local-manager.png)

The local manager component is deployed on every compute host and is invoked periodically to
determine when it necessary to reallocate VM instances from the host. A high-level view of the
workflow performed by the local manager is shown in Figure 3. First of all, it reads from the local
storage the historical data about the resource usage by the VMs stored by the data collector
described in the next section. Then, the local manager invokes the specified in the configuration
underload detection algorithm to determine whether the host is underloaded. If the host is
underloaded, the local manager sends a request to the global manager's REST interface to migrate all
the VMs from the host and switch the host to the sleep mode.

If the host is not underloaded, the local manager proceeds to invoking the specified in the
configuration overload detection algorithm. If the host is overloaded, the local manager invokes the
configured VM selection algorithm to select the VMs to migrate from the host. Once the VMs to
migrate from the host are selected, the local manager sends a request to the global manager's REST
interface to migrate the selected VMs from the host.

The local manager also exposes a REST interface to receive acknowledgments from the global manager
when the requested VM migrations are completed. Upon receiving an acknowledgment, the local manager
removes from the local data store the data about the resource usage of the VMs migrated from the
host.

Similarly to the global manager, the local manager can be configured to use specific underload
detection, overload detection, and VM selection algorithm using the configuration file discussed
further in the paper.


#### Underload Detection.

Underload detection is done by a specified in the configuration underload detection algorithm. The
algorithm has a pre-defined interface, which allows substituting different implementations of the
algorithm. The configured algorithm is invoked by the local manager and accepts the historical data
about the resource usage by the VMs running on the host as an input. An underload detection
algorithm returns a decision of whether the host is underloaded.


#### Overload Detection.

Overload detection is done by a specified in the configuration overload detection algorithm.
Similarly to underload detection, all overload detection algorithms implement a pre-defined
interface to enable configuration-driven substitution of difference implementations. The configured
algorithm is invoked by the local manager and accepts the historical data about the resource usage
by the VMs running on the host as an input. An overload detection algorithm returns a decision of
whether the host is overloaded.


#### VM Selection.

If a host is overloaded, it is necessary to select VMs to migrate from the host to avoid performance
degradation. This is done by a specified in the configuration VM selection algorithm. Similarly to
underload and overload detection algorithms, different VM selection algorithm can plugged in
according to configuration. A VM selection algorithm accepts the historical data about the resource
usage the VMs running on the host and returns a set of VMs to migrate from the host.


### Data Collector

The data collector is deployed on every compute host and is executed periodically to collect the CPU
utilization data for each VM running on the host and stores it in the local file-based data store.
The data is collected in average number of MHz consumed by a VM during the last measurement
interval. The CPU usage data are stored as integers. This data format is portable: the collected
values can be converted to the CPU utilization for any host or VM type, supporting heterogeneous
hosts and VMs.

The actual data is obtained from Libvirt in the form of the CPU time consumed by a VM to date. Using
the CPU time collected at the previous time frame, the CPU time for the past time interval is
calculated. According to the CPU frequency of the host and the length of the time interval, the CPU
time is converted into the required average MHz consumed by the VM over the last time interval. The
collected data are stored both locally and submitted to the central database.


## Data Stores

As shown in Figure 1, the system contains two types of data stores:

- *Central database* -- a database deployed on the management host.
- *Local file-based data storage* -- a data store deployed on every compute host and used for
   storing resource usage data to use by local managers.


### Central Database

The `vms` table for storing the mapping between UUIDs of VMs and the internal IDs:

```
CREATE TABLE vm_resource_usage (
     id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
     uuid CHAR(36) NOT NULL,
     PRIMARY KEY (id)
) ENGINE=MyISAM;
```

- `id` -- the auto incremented ID of the VM;
- `uuid` -- the UUID of the VM.


The `vm_resource_usage` table is for storing the data about resource usage by VMs:

```
CREATE TABLE vm_resource_usage (
     id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
     vm_id BIGINT UNSIGNED NOT NULL,
     timestamp TIMESTAMP NOT NULL,
     cpu_mhz MEDIUMINT UNSIGNED NOT NULL,
     PRIMARY KEY (id)
) ENGINE=MyISAM;
```

- `id` -- the auto incremented record ID;
- `vm_id` -- the foreign key referring the `vms` table;
- `timestamp` -- the time of the data collection;
- `cpu_mhz` -- the collected average CPU usage in MHz from the last measurement to the
  current time stamp.


### Local File-Based Data Store

The data collector stores the resource usage information locally in files in the
`<local_data_directory>/vm`. The data collector stores the data in separate files for each VM. The
UUIDs of the VMs are used as the file names for storing data from the respective VMs. The format of
files is a new line separated list of integers representing the CPU consumption by the VMs in MHz.


## Configuration File

The configuration of OpenStack Neat is stored in `/etc/neat/neat.conf` in the standard ini format.
The configuration includes the following options:

- `sql_connection` -- the host and credentials for connecting to the MySQL database;
- `admin_tenant_name` -- the admin tenant name for authentication with Nova using Keystone;
- `admin_user` -- the admin user name for authentication with Nova using Keystone;
- `admin_password` -- the admin password for authentication with Nova using Keystone;
- `global_manager_host` -- the host name of the global manager;
- `global_magager_port` -- the port of the global manager's REST interface;
- `local_data_directory` -- the directory, where the data collector stores the data on the resource
  usage by the VMs running on the host, the default is `/var/lib/neat`;


## TODO

- What data should be collected by the Data Collector?
- What data should be stored locally by the Data Collector?
- What is the format of the data?
- What data should be submitted to the database?
- What is the database schema?
- Define REST APIs for the Global and Local Managers
- Find out how to remotely switch hosts on or off


# Implementation

This section should describe a plan of action (the "how") to implement the changes discussed. Could
include subsections like:

## Libraries

- [pyqcy](https://github.com/Xion/pyqcy) -- a QuickCheck-like testing framework for Python.
- [PyContracts](http://andreacensi.github.com/contracts/) -- a Python library for Design by Contract
  (DbC).
- [SQLAlchemy](http://www.sqlalchemy.org/) -- a Python SQL toolkit and Object Relational Mapper, it
  is used by OpenStack.
- [Bottle](http://bottlepy.org/) -- a micro web-framework for Python, authentication using the same
  credentials using for Nova.
- [python-novaclient](https://github.com/openstack/python-novaclient) -- a python client API to Nova.
- [Sphinx](http://sphinx.pocoo.org/) -- a documentation generator for Python.


## UI Changes

Should cover changes required to the UI, or specific UI that is required to implement this


## Code Changes

Code changes should include an overview of what needs to change, and in some cases even the specific
details.


## Migration

Include:

- data migration, if any
- redirects from old URLs to new ones, if any
- how users will be pointed to the new way of doing things, if necessary.


# Test/Demo Plan

This need not be added or completed until the specification is nearing beta.


# Unresolved issues

This should highlight any issues that should be addressed in further specifications, and not
problems with the specification itself; since any specification with problems cannot be approved.


# BoF agenda and discussion

Use this section to take notes during the BoF; if you keep it in the approved spec, use it for
summarising what was discussed and note any options that were rejected.


# References
