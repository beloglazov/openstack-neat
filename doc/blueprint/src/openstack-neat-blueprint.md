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
just one the hosts. Then, one of the VMs can be migrated to the host serving the other VM, and the
idle host can be switched to the sleep mode to save energy.

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
consolidation of VMs within OpenStack environments. The framework should provide an overall
architecture and abstract interfaces of components implementing the 4 decision-making algorithms
listed above. The framework should allow configuration-driven plugging in particular implementations
of the decision-making algorithms. The implementation of the framework will include the algorithms
proposed in our previous works [@beloglazov2012optimal; @beloglazov2012overload].



# Release Note

The functionality covered by this project will be implemented in the form of services separate from
the core OpenStack services. The services of this project will interact with the core OpenStack
services using their public APIs. It will be required to create a new Keystone user within the
`service` tenant. The project will also require a new MySQL database for storing information on the
host configuration, VM placement, and CPU utilization by the VMs. The project will provide script
for automated initialization of the database. The service of the project will need to be run on the
management and compute hosts.


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
center resources, as demonstrated by numerous studies
[@nathuji2007virtualpower; @verma2008pmapper; @zhu20081000; @gmach2008integrated; @gmach2009resource; @vmware2010distributed; @jung2010mistral; @jung2010mistral; @kumar2009vmanage; @guenter2011managing; @bobroff2007dynamic; @beloglazov2011taxonomy].
In this project, we aim to implement an extensible framework for dynamic VM consolidation
specifically targeted at OpenStack.


# User stories

- As a Cloud Administrator or Systems Integrator, I want to support dynamic VM consolidation to
  improve the utilization of physical resources and reduce the energy consumption.
- As a Cloud Administrator, I want to provide QoS guarantees to the consumers.
- As a Cloud Administrator, I want to minimize the price of the service provided for the consumers
  by reducing the operating costs through the reduced energy consumption.
- As a Cloud Administrator, I want to decrease the carbon dioxide emissions into the environment by
  reducing the energy consumption by the data center's resources.
- As a Cloud Service Consumer, I want to pay the minimum price for the service provided through the
  minimized energy consumption of the computing resources.
- As a Cloud Service Consumer, I want to use Green Cloud resources, whose provider strives to reduce
  the impact on the environment.


# Assumptions

Glance ''stores'' the server template and metadata map; Nova must ''implement'' the server template.


# Design

This is just one possible design for this feature (keep that in mind). At its simplest, a server
template consists of a core image and a ''metadata map''. The metadata map defines metadata that
must be collected during server creation and a list of files (on the server) that must be modified
using the defined metadata.

Here is a simple example: let's assume that the server template has a Linux server with Apache HTTP
installed. Apache needs to know the IP address of the server and the directory on the server that
contains the HTML files.

The metadata map would look something like this:

```
  metadata {
   IP_ADDRESS;
   HTML_ROOT : string(1,255) : "/var/www/";
  }
  map {
   /etc/httpd/includes/server.inc
  }
```

In this case, the {{{metadata}}} section defines the metadata components required; the {{{map}}}
section defines the files that must be parsed and have the metadata configured. Within the
{{{metadata}}} section, there are two defined items. {{{IP_ADDRESS}}} is a predefined (built-in)
value, and {{{HTML_ROOT}}} is the root directory of the web server.

For {{{HTML_ROOT}}}, there are three sub-fields: the name, the data type, and (in this case) the
default value. The token {{{required}}} could be used for items that must be supplied by the user.

When the server is created, a (as-yet-undefined) process would look at the files in the {{{map}}}
section and replace metadata tokens with the defined values. For example, the file might contain:

```
<VirtualHost {{IP_ADDRESS}}:*>
  DocumentRoot "{{HTML_ROOT}}";
</VirtualHost>
```


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
