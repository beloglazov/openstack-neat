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

""" The main data collector module.

The data collector is deployed on every compute host and is executed
periodically to collect the CPU utilization data for each VM running
on the host and stores the data in the local file-based data store.
The data is stored as the average number of MHz consumed by a VM
during the last measurement interval. The CPU usage data are stored as
integers. This data format is portable: the stored values can be
converted to the CPU utilization for any host or VM type, supporting
heterogeneous hosts and VMs.

The actual data is obtained from Libvirt in the form of the CPU time
consumed by a VM to date. Using the CPU time collected at the previous
time frame, the CPU time for the past time interval is calculated.
According to the CPU frequency of the host and the length of the time
interval, the CPU time is converted into the required average MHz
consumed by the VM over the last time interval. The collected data are
stored both locally and submitted to the central database. The number
of the latest data values stored locally and passed to the underload /
overload detection and VM selection algorithms is defined using the
`data_collector_data_length` option in the configuration file.

At the beginning of every execution, the data collector obtains the
set of VMs currently running on the host using the Nova API and
compares them to the VMs running on the host at the previous time
step. If new VMs have been found, the data collector fetches the
historical data about them from the central database and stores the
data in the local file-based data store. If some VMs have been
removed, the data collector removes the data about these VMs from the
local data store.

The data collector stores the resource usage information locally in
files in the <local_data_directory>/vm directory, where
<local_data_directory> is defined in the configuration file using
the local_data_directory option. The data for each VM are stored in
a separate file named according to the UUID of the corresponding VM.
The format of the files is a new line separated list of integers
representing the average CPU consumption by the VMs in MHz during the
last measurement interval.

The data collector will be implemented as a Linux daemon running in
the background and collecting data on the resource usage by VMs every
data_collector_interval seconds. When the data collection phase is
invoked, the component performs the following steps:

1. Read the names of the files from the <local_data_directory>/vm
   directory to determine the list of VMs running on the host at the
   last data collection.

2. Call the Nova API to obtain the list of VMs that are currently
   active on the host.

3. Compare the old and new lists of VMs and determine the newly added
   or removed VMs.

4. Delete the files from the <local_data_directory>/vm directory
   corresponding to the VMs that have been removed from the host.

5. Fetch the latest data_collector_data_length data values from the
   central database for each newly added VM using the database
   connection information specified in the sql_connection option and
   save the data in the <local_data_directory>/vm directory.

6. Call the Libvirt API to obtain the CPU time for each VM active on
   the host.

7. Transform the data obtained from the Libvirt API into the average
   MHz according to the frequency of the host's CPU and time interval
   from the previous data collection.

8. Store the converted data in the <local_data_directory>/vm
   directory in separate files for each VM, and submit the data to the
   central database.

9. Schedule the next execution after data_collector_interval
   seconds.
"""

from contracts import contract
from neat.contracts_extra import *

from neat.config import *
from neat.db_utils import *


@contract
def start(iterations):
    """ Start the data collector loop.

    :param iterations: The number of iterations to perform, -1 for infinite.
     :type iterations: int

    :return: The number of iterations performed.
     :rtype: int
    """
    config = read_config([DEFAILT_CONFIG_PATH, CONFIG_PATH])
    if not validate_config(config, REQUIRED_FIELDS):
        raise KeyError("The config dictionary does not contain all the required fields")

    if iterations == -1:
        while True:
            collect(config)
    else:
        for _ in xrange(iterations):
            collect(config)
    return iterations


def collect(config):
    """ Execute a data collection iteration.

1. Read the names of the files from the <local_data_directory>/vm
   directory to determine the list of VMs running on the host at the
   last data collection.

2. Call the Nova API to obtain the list of VMs that are currently
   active on the host.

3. Compare the old and new lists of VMs and determine the newly added
   or removed VMs.

4. Delete the files from the <local_data_directory>/vm directory
   corresponding to the VMs that have been removed from the host.

5. Fetch the latest data_collector_data_length data values from the
   central database for each newly added VM using the database
   connection information specified in the sql_connection option and
   save the data in the <local_data_directory>/vm directory.

6. Call the Libvirt API to obtain the CPU time for each VM active on
   the host.

7. Transform the data obtained from the Libvirt API into the average
   MHz according to the frequency of the host's CPU and time interval
   from the previous data collection.

8. Store the converted data in the <local_data_directory>/vm
   directory in separate files for each VM, and submit the data to the
   central database.

9. Schedule the next execution after data_collector_interval
   seconds.

    :param config: A config dictionary.
     :type config: dict(str: *)
    """
    vms_previous = get_previous_vms(
        build_local_vm_path(config.get('local_data_directory')))
    vms_current = get_current_vms()
    vms_added = get_added_vms(vms_previous, vms_current)
    vms_removed = get_removed_vms(vms_previous, vms_current)
    cleanup_local_data(vms_removed)


@contract
def get_previous_vms(path):
    """ Get a list of VM UUIDs from the path.

    :param path: A path to read VM UUIDs from.
     :type path: str

    :return: The list of VM UUIDs from the path.
     :rtype: list(str)
    """
    return os.listdir(path)


@contract()
def get_current_vms(vir_connection):
    """ Get a list of VM UUIDs from libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :return: The list of VM UUIDs from libvirt.
     :rtype: list(str)
    """
    vm_uuids = []
    for vm_id in vir_connection.listDomainsID():
        vm_uuids.append(vir_connection.lookupByID(vm_id).UUIDString())
    return vm_uuids


@contract
def build_local_vm_path(local_data_directory):
    """ Build the path to the local VM data directory.

    :param local_data_directory: The base local data path.
     :type local_data_directory: str

    :return: The path to the local VM data directory.
     :rtype: str
    """
    return os.path.join(local_data_directory, 'vms')


@contract
def get_added_vms(previous_vms, current_vms):
    """ Get a list of newly added VM UUIDs.

    :param previous_vms: A list of VMs at the previous time frame.
     :type previous_vms: list(str)

    :param current_vms: A list of VM at the current time frame.
     :type current_vms: list(str)

    :return: A list of VM UUIDs that have been added since the last time frame.
     :rtype: list(str)
    """
    return substract_lists(current_vms, previous_vms)


@contract
def get_removed_vms(previous_vms, current_vms):
    """ Get a list of VM UUIDs removed since the last time frame.

    :param previous_vms: A list of VMs at the previous time frame.
     :type previous_vms: list(str)

    :param current_vms: A list of VM at the current time frame.
     :type current_vms: list(str)

    :return: A list of VM UUIDs that have been removed since the last time frame.
     :rtype: list(str)
    """
    return substract_lists(previous_vms, current_vms)


@contract
def substract_lists(list1, list2):
    """ Return the elements of list1 that are not in list2.

    :param list1: The first list.
     :type list1: list

    :param list2: The second list.
     :type list2: list

    :return: The list of element of list 1 that are not in list2.
     :rtype: list
    """
    return list(set(list1).difference(list2))


@contract
def cleanup_local_data(path, vms):
    """ Delete the local data related to the removed VMs.

    :param path: A path to removed VM data from.
     :type path: str

    :param vms: A list of removed VM UUIDs.
     :type vms: list(str)
    """
    for vm in vms:
        os.remove(os.path.join(path, vm))


@contract
def fetch_remote_data(db, data_length, vms):
    """ Fetch VM data from the central DB.

    :param db: The database object.
     :type db: Database

    :param data_length: The length of data to fetch.
     :type data_length: int

    :param vms: A list of VM UUIDs to fetch data for.
     :type vms: list(str)

    :return: A dictionary of VM UUIDs and the corresponding data.
     :rtype: dict(str : list(int))
    """
    pass


def getNumberOfPhysicalCpus(connection):
    return connection.getInfo()[2]


def getDomainTotalCpuTime(domain):
    return domain.getCPUStats(True, 0)[0]['cpu_time']


def getCpuUtilization(numberOfPhysicalCpus, domain, previousTime, previousCpuTime, currentTime, currentCpuTime):
    #prevTime = time.time()
    #prevCpuTime = getDomainTotalCpuTime(domain)
    #time.sleep(1)
    #currTime = time.time()
    #currCpuTime = getDomainTotalCpuTime(domain)

    return ((currentCpuTime - previousCpuTime) / ((currentTime - previousTime) * 1000000000 * numberOfPhysicalCpus))


def collectCpuUtilization(numberOfPhysicalCpus, timeInterval, reportingFunction):
    pass

# temporarily commented
#conn = libvirt.openReadOnly(None)
#if conn is None:
#    print 'Failed to open connection to the hypervisor'
#    sys.exit(1)
#
#numberOfPhysicalCpus = getNumberOfPhysicalCpus(conn)








#print "Host CPUs: " + str(numberOfPhysicalCpus)




#getCpuUtilization(dom0, numberOfPhysicalCpus)


#try:
#    dom0 = conn.lookupByName("cirros")
#except:
#    print 'Failed to find the main domain'
#    sys.exit(1)


#print "Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType())
#print dom0.info()
#print dom0.getCPUStats(1, 0)
#print dom0.vcpus()
#print dom0.vcpuPinInfo(0)
#print conn.getCPUStats(1, 0)
