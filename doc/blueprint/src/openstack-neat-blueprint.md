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

## Components

### Data Collector

- Runs on every Nova Compute host periodically (every X seconds)
- Collects the CPU utilization data for every VM running on the host
- Submits the collected data to the central database
- Stores the collected data locally in a file


### Local Manager

- Runs on every Nova Compute host periodically (every X seconds)
- Invokes decision making algorithm
- Reads the data stored by the Data Collector
- Invokes the Underload Detector
    - If the host is underloaded, sends a request to the Global Manager to migrate all the VMs away
      from the host and switch the host to the sleep mode, then exit
    - If the host is not underloaded, continue with the next steps
- Invokes the Overload Detector
    - If the host is overloaded, invoke the VM Selector
 	    - Send a request to the Global Manager to migrate the VMs selected by the VM Selector
	- Exit
- Processes acknowledgment requests from the Global Manager about completion of VM migrations and
  removes/adds records about the migrated VM


### Underload Detector

- Deployed on every Nova Compute host
- Invoked by the Local Manager
- Configured with a specific underload detection algorithm
- Passed with the data read by the Local Manager as an argument
- Invokes the specified underload detection algorithm and passes the data passed by the Local
  Manager as an argument
- Returns the decision of the underload detection algorithm of whether the host underloaded


### Overload Detector

- Deployed on every Nova Compute host
- Invoked by the Local Manager
- Configured with a specific overload detection algorithm
- Passed with the data read by the Local Manager as an argument
- Invokes the specified overload detection algorithm and passes the data passed by the Local
  Manager as an argument
- Returns the decision of the overload detection algorithm of whether the host overloaded

### VM Selector

- Deployed on every Nova Compute host
- Invoked by the Local Manager if the host is overloaded
- Configured with a specific VM selection algorithm
- Invokes the specified VM selection algorithm and passes the data passed by the Local Manager as an
  argument
- Returns the set of VM to migrate returned by the invoked VM selection algorithm


### Global Manager

- Runs on the management host
- Configured with a VM placement algorithm
- Processes VM migration requests received from Local Managers
- If required, switches hosts on or off
- Invokes the specified VM placement algorithm to determine destination hosts for VM migrations
	- VM placement algorithm can directly query the database to obtain the required information, such
      as the current VM placement, and resource utilization
- Once destination hosts are determines, call the Nova API to migrate VMs
- Once a migration is completed, send an acknowledgment request to the Local Managers of the source
  and destination hosts


## TODO

- What data should be stored locally by the Data Collector?
- What is the format of the data?
- What data should be submitted to the database?
- What is the database schema?
- Define REST APIs for the Global and Local Managers
- Find out how to remotely switch hosts on or off


# Implementation

This section should describe a plan of action (the "how") to implement the changes discussed. Could
include subsections like:


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
