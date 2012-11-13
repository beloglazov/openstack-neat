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

import os
import time
from collections import deque
import libvirt

import neat.common as common
from neat.config import *
from neat.db_utils import *

import logging
log = logging.getLogger(__name__)


@contract
def start():
    """ Start the data collector loop.

    :return: The final state.
     :rtype: dict(str: *)
    """
    config = read_and_validate_config([DEFAILT_CONFIG_PATH, CONFIG_PATH],
                                      REQUIRED_FIELDS)

    common.init_logging(
        config['log_directory'],
        'data-collector.log',
        int(config['log_level']))

    vm_path = common.build_local_vm_path(config['local_data_directory'])
    if not os.access(vm_path, os.F_OK):
        os.makedirs(vm_path)
        log.info('Created a local VM data directory: %s', vm_path)
    else:
        cleanup_all_local_data(config['local_data_directory'])
        log.info('Creaned up the local data directory: %s',
                 config['local_data_directory'])

    interval = config['data_collector_interval']
    log.info('Starting the data collector, ' +
             'iterations every %s seconds', interval)
    return common.start(
        init_state,
        execute,
        config,
        int(interval))


@contract
def init_state(config):
    """ Initialize a dict for storing the state of the data collector.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :return: A dict containing the initial state of the data collector.
     :rtype: dict
    """
    vir_connection = libvirt.openReadOnly(None)
    if vir_connection is None:
        message = 'Failed to open a connection to the hypervisor'
        log.critical(message)
        raise OSError(message)

    hostname = vir_connection.getHostname()
    host_cpu_mhz, host_ram = get_host_characteristics(vir_connection)
    physical_cpus = common.physical_cpu_count(vir_connection)
    host_cpu_usable_by_vms = float(config['host_cpu_usable_by_vms'])

    db = init_db(config['sql_connection'])
    db.update_host(hostname,
                   int(host_cpu_mhz * host_cpu_usable_by_vms),
                   physical_cpus,
                   host_ram)

    return {'previous_time': 0.,
            'previous_cpu_time': dict(),
            'previous_cpu_mhz': dict(),
            'previous_host_cpu_time_total': 0.,
            'previous_host_cpu_time_busy': 0.,
            'previous_overload': -1,
            'vir_connection': vir_connection,
            'hostname': hostname,
            'host_cpu_overload_threshold':
                float(config['host_cpu_overload_threshold']) * \
                host_cpu_usable_by_vms,
            'physical_cpus': physical_cpus,
            'physical_cpu_mhz': host_cpu_mhz,
            'physical_core_mhz': host_cpu_mhz / physical_cpus,
            'db': db}


def execute(config, state):
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
   the host. Transform the data obtained from the Libvirt API into the
   average MHz according to the frequency of the host's CPU and time
   interval from the previous data collection.

8. Store the converted data in the <local_data_directory>/vm
   directory in separate files for each VM, and submit the data to the
   central database.

    :param config: A config dictionary.
     :type config: dict(str: *)

    :param state: A state dictionary.
     :type state: dict(str: *)

    :return: The updated state dictionary.
     :rtype: dict(str: *)
    """
    log.info('Started an iteration')
    vm_path = common.build_local_vm_path(config['local_data_directory'])
    host_path = common.build_local_host_path(config['local_data_directory'])
    data_length = int(config['data_collector_data_length'])
    vms_previous = get_previous_vms(vm_path)
    vms_current = get_current_vms(state['vir_connection'])

    vms_added = get_added_vms(vms_previous, vms_current.keys())
    added_vm_data = dict()
    if vms_added:
        if log.isEnabledFor(logging.DEBUG):
            log.debug('Added VMs: %s', str(vms_added))

        for i, vm in enumerate(vms_added):
            if vms_current[vm] != libvirt.VIR_DOMAIN_RUNNING:
                del vms_added[i]
                del vms_current[vm]
                if log.isEnabledFor(logging.DEBUG):
                    log.debug('Added VM %s skipped as migrating in', vm)

        added_vm_data = fetch_remote_data(state['db'],
                                          data_length,
                                          vms_added)
        if log.isEnabledFor(logging.DEBUG):
            log.debug('Fetched remote data: %s', str(added_vm_data))
        write_vm_data_locally(vm_path, added_vm_data, data_length)

    vms_removed = get_removed_vms(vms_previous, vms_current.keys())
    if vms_removed:
        if log.isEnabledFor(logging.DEBUG):
            log.debug('Removed VMs: %s', str(vms_removed))
        cleanup_local_vm_data(vm_path, vms_removed)
        for vm in vms_removed:
            del state['previous_cpu_time'][vm]
            del state['previous_cpu_mhz'][vm]

    log.info('Started VM data collection')
    current_time = time.time()
    (cpu_time, cpu_mhz) = get_cpu_mhz(state['vir_connection'],
                                      state['physical_core_mhz'],
                                      state['previous_cpu_time'],
                                      state['previous_time'],
                                      current_time,
                                      vms_current.keys(),
                                      state['previous_cpu_mhz'],
                                      added_vm_data)
    log.info('Completed VM data collection')

    log.info('Started host data collection')
    (host_cpu_time_total,
     host_cpu_time_busy,
     host_cpu_mhz) = get_host_cpu_mhz(state['physical_cpu_mhz'],
                                      state['previous_host_cpu_time_total'],
                                      state['previous_host_cpu_time_busy'])
    log.info('Completed host data collection')

    if state['previous_time'] > 0:
        append_vm_data_locally(vm_path, cpu_mhz, data_length)
        append_vm_data_remotely(state['db'], cpu_mhz)

        host_cpu_mhz_hypervisor = host_cpu_mhz - sum(cpu_mhz.values())
        if host_cpu_mhz_hypervisor < 0:
            host_cpu_mhz_hypervisor = 0
        append_host_data_locally(host_path, host_cpu_mhz_hypervisor, data_length)
        append_host_data_remotely(state['db'],
                                  state['hostname'],
                                  host_cpu_mhz_hypervisor)

        if log.isEnabledFor(logging.DEBUG):
            log.debug('Collected VM CPU MHz: %s', str(cpu_mhz))
            log.debug('Collected host CPU MHz: %s', str(host_cpu_mhz_hypervisor))

        state['previous_overload'] = log_host_overload(
            state['db'],
            state['host_cpu_overload_threshold'],
            state['hostname'],
            state['previous_overload'],
            state['physical_cpu_mhz'],
            cpu_mhz.values())

    state['previous_time'] = current_time
    state['previous_cpu_time'] = cpu_time
    state['previous_cpu_mhz'] = cpu_mhz
    state['previous_host_cpu_time_total'] = host_cpu_time_total
    state['previous_host_cpu_time_busy'] = host_cpu_time_busy

    log.info('Completed an iteration')
    return state


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
    """ Get a dict of VM UUIDs to states from libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :return: The dict of VM UUIDs to states from libvirt.
     :rtype: dict(str: int)
    """
    vm_uuids = {}
    for vm_id in vir_connection.listDomainsID():
        try:
            vm = vir_connection.lookupByID(vm_id)
            vm_uuids[vm.UUIDString()] = vm.state(0)[0]
        except libvirt.libvirtError:
            pass
    return vm_uuids


@contract
def get_added_vms(previous_vms, current_vms):
    """ Get a list of newly added VM UUIDs.

    :param previous_vms: A list of VMs at the previous time frame.
     :type previous_vms: list(str)

    :param current_vms: A list of VM at the current time frame.
     :type current_vms: list(str)

    :return: A list of VM UUIDs added since the last time frame.
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

    :return: A list of VM UUIDs removed since the last time frame.
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
def cleanup_local_vm_data(path, vms):
    """ Delete the local data related to the removed VMs.

    :param path: A path to remove VM data from.
     :type path: str

    :param vms: A list of removed VM UUIDs.
     :type vms: list(str)
    """
    for vm in vms:
        os.remove(os.path.join(path, vm))


@contract
def cleanup_all_local_data(path):
    """ Delete all the local data about VMs.

    :param path: A path to the local data directory.
     :type path: str
    """
    vm_path = common.build_local_vm_path(path)
    cleanup_local_vm_data(vm_path, os.listdir(vm_path))
    host_path = common.build_local_host_path(path)
    if os.access(host_path, os.F_OK):
        os.remove(host_path)


@contract
def fetch_remote_data(db, data_length, uuids):
    """ Fetch VM data from the central DB.

    :param db: The database object.
     :type db: Database

    :param data_length: The length of data to fetch.
     :type data_length: int

    :param uuids: A list of VM UUIDs to fetch data for.
     :type uuids: list(str)

    :return: A dictionary of VM UUIDs and the corresponding data.
     :rtype: dict(str : list(int))
    """
    result = dict()
    for uuid in uuids:
        result[uuid] = db.select_cpu_mhz_for_vm(uuid, data_length)
    return result


@contract
def write_vm_data_locally(path, data, data_length):
    """ Write a set of CPU MHz values for a set of VMs.

    :param path: A path to write the data to.
     :type path: str

    :param data: A map of VM UUIDs onto the corresponing CPU MHz history.
     :type data: dict(str : list(int))

    :param data_length: The maximum allowed length of the data.
     :type data_length: int
    """
    for uuid, values in data.items():
        with open(os.path.join(path, uuid), 'w') as f:
            if data_length > 0:
                f.write('\n'.join([str(x)
                                   for x in values[-data_length:]]) + '\n')


@contract
def append_vm_data_locally(path, data, data_length):
    """ Write a CPU MHz value for each out of a set of VMs.

    :param path: A path to write the data to.
     :type path: str

    :param data: A map of VM UUIDs onto the corresponing CPU MHz values.
     :type data: dict(str : int)

    :param data_length: The maximum allowed length of the data.
     :type data_length: int
    """
    for uuid, value in data.items():
        vm_path = os.path.join(path, uuid)
        if not os.access(vm_path, os.F_OK):
            with open(vm_path, 'w') as f:
                f.write(str(value) + '\n')
        else:
            with open(vm_path, 'r+') as f:
                values = deque(f.read().strip().splitlines(), data_length)
                values.append(value)
                f.truncate(0)
                f.seek(0)
                f.write('\n'.join([str(x) for x in values]) + '\n')


@contract
def append_vm_data_remotely(db, data):
    """ Submit CPU MHz values to the central database.

    :param db: The database object.
     :type db: Database

    :param data: A map of VM UUIDs onto the corresponing CPU MHz values.
     :type data: dict(str : int)
    """
    db.insert_vm_cpu_mhz(data)


@contract
def append_host_data_locally(path, cpu_mhz, data_length):
    """ Write a CPU MHz value for the host.

    :param path: A path to write the data to.
     :type path: str

    :param cpu_mhz: A CPU MHz value.
     :type cpu_mhz: int,>=0

    :param data_length: The maximum allowed length of the data.
     :type data_length: int
    """
    if not os.access(path, os.F_OK):
        with open(path, 'w') as f:
            f.write(str(cpu_mhz) + '\n')
    else:
        with open(path, 'r+') as f:
            values = deque(f.read().strip().splitlines(), data_length)
            values.append(cpu_mhz)
            f.truncate(0)
            f.seek(0)
            f.write('\n'.join([str(x) for x in values]) + '\n')


@contract
def append_host_data_remotely(db, hostname, host_cpu_mhz):
    """ Submit a host CPU MHz value to the central database.

    :param db: The database object.
     :type db: Database

    :param hostname: The host name.
     :type hostname: str

    :param host_cpu_mhz: An average host CPU utilization in MHz.
     :type host_cpu_mhz: int,>=0
    """
    db.insert_host_cpu_mhz(hostname, host_cpu_mhz)


@contract
def get_cpu_mhz(vir_connection, physical_core_mhz, previous_cpu_time,
                previous_time, current_time, current_vms, 
                previous_cpu_mhz, added_vm_data):
    """ Get the average CPU utilization in MHz for a set of VMs.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :param physical_core_mhz: The core frequency of the physical CPU in MHz.
     :type physical_core_mhz: int

    :param previous_cpu_time: A dict of previous CPU times for the VMs.
     :type previous_cpu_time: dict(str : number)

    :param previous_time: The previous timestamp.
     :type previous_time: float

    :param current_time: The previous timestamp.
     :type current_time: float

    :param current_vms: A list of VM UUIDs.
     :type current_vms: list(str)

    :param previous_cpu_mhz: A dict of VM UUIDs and previous CPU MHz.
     :type previous_cpu_mhz: dict(str : int)

    :param added_vm_data: A dict of VM UUIDs and the corresponding data.
     :type added_vm_data: dict(str : list(int))

    :return: The updated CPU times and average CPU utilization in MHz.
     :rtype: tuple(dict(str : number), dict(str : int))
    """
    previous_vms = previous_cpu_time.keys()
    added_vms = get_added_vms(previous_vms, current_vms)
    removed_vms = get_removed_vms(previous_vms, current_vms)
    cpu_mhz = {}

    for uuid in removed_vms:
        del previous_cpu_time[uuid]

    for uuid, cpu_time in previous_cpu_time.items():
        current_cpu_time = get_cpu_time(vir_connection, uuid)
        if current_cpu_time < cpu_time:
            if log.isEnabledFor(logging.DEBUG):
                log.debug('VM %s: current_cpu_time < cpu_time: ' + 
                          'previous CPU time %d, ' +
                          'current CPU time %d, ' +
                          uuid, cpu_time, current_cpu_time)
                log.debug('VM %s: using previous CPU MHz %d, ' +
                          uuid, previous_cpu_mhz[uuid])
            cpu_mhz[uuid] = previous_cpu_mhz[uuid]
        else:
            if log.isEnabledFor(logging.DEBUG):
                log.debug('VM %s: previous CPU time %d, ' +
                          'current CPU time %d, ' +
                          'previous time %.10f, ' +
                          'current time %.10f',
                          uuid, cpu_time, current_cpu_time, 
                          previous_time, current_time)
            cpu_mhz[uuid] = calculate_cpu_mhz(physical_core_mhz, previous_time,
                                              current_time, cpu_time,
                                              current_cpu_time)
        previous_cpu_time[uuid] = current_cpu_time
        if log.isEnabledFor(logging.DEBUG):
            log.debug('VM %s: CPU MHz %d', uuid, cpu_mhz[uuid])

    for uuid in added_vms:
        if added_vm_data[uuid]:
            cpu_mhz[uuid] = added_vm_data[uuid][-1]
        previous_cpu_time[uuid] = get_cpu_time(vir_connection, uuid)

    return previous_cpu_time, cpu_mhz


@contract
def get_cpu_time(vir_connection, uuid):
    """ Get the CPU time of a VM specified by the UUID using libvirt.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :param uuid: The UUID of a VM.
     :type uuid: str[36]

    :return: The CPU time of the VM.
     :rtype: number,>=0
    """
    try:
        domain = vir_connection.lookupByUUIDString(uuid)
        return domain.getCPUStats(True, 0)[0]['cpu_time']
    except libvirt.libvirtError:
        return 0.


@contract
def calculate_cpu_mhz(cpu_mhz, previous_time, current_time,
                      previous_cpu_time, current_cpu_time):
    """ Calculate the average CPU utilization in MHz for a period of time.

    :param cpu_mhz: The frequency of a core of the physical CPU in MHz.
     :type cpu_mhz: int

    :param previous_time: The previous time.
     :type previous_time: float

    :param current_time: The current time.
     :type current_time: float

    :param previous_cpu_time: The previous CPU time of the domain.
     :type previous_cpu_time: number

    :param current_cpu_time: The current CPU time of the domain.
     :type current_cpu_time: number

    :return: The average CPU utilization in MHz.
     :rtype: int,>=0
    """
    return int(cpu_mhz * float(current_cpu_time - previous_cpu_time) / \
               ((current_time - previous_time) * 1000000000))


@contract
def get_host_cpu_mhz(cpu_mhz, previous_cpu_time_total, previous_cpu_time_busy):
    """ Get the average CPU utilization in MHz for a set of VMs.

    :param cpu_mhz: The total frequency of the physical CPU in MHz.
     :type cpu_mhz: int

    :param previous_cpu_time_total: The previous total CPU time.
     :type previous_cpu_time_total: float

    :param previous_cpu_time_busy: The previous busy CPU time.
     :type previous_cpu_time_busy: float

    :return: The current total and busy CPU time, and CPU utilization in MHz.
     :rtype: tuple(float, float, int)
    """
    cpu_time_total, cpu_time_busy = get_host_cpu_time()
    cpu_usage = int(cpu_mhz * (cpu_time_busy - previous_cpu_time_busy) / \
                    (cpu_time_total - previous_cpu_time_total))
    if cpu_usage < 0:
        raise ValueError('The host CPU usage in MHz must be >=0, but it is: ' + str(cpu_usage) +
                         '; cpu_mhz=' + str(cpu_mhz) +
                         '; previous_cpu_time_total=' + str(previous_cpu_time_total) +
                         '; cpu_time_total=' + str(cpu_time_total) +
                         '; previous_cpu_time_busy=' + str(previous_cpu_time_busy) +
                         '; cpu_time_busy=' + str(cpu_time_busy))
    return cpu_time_total, \
           cpu_time_busy, \
           cpu_usage


@contract()
def get_host_cpu_time():
    """ Get the total and busy CPU time of the host.

    :return: A tuple of the total and busy CPU time.
     :rtype: tuple(float, float)
    """
    with open('/proc/stat', 'r') as f:
        values = [float(x) for x in f.readline().split()[1:8]]
        return sum(values), sum(values[0:3])


@contract()
def get_host_characteristics(vir_connection):
    """ Get the total CPU MHz and RAM of the host.

    :param vir_connection: A libvirt connection object.
     :type vir_connection: virConnect

    :return: A tuple of the total CPU MHz and RAM of the host.
     :rtype: tuple(int, int)
    """
    info = vir_connection.getInfo()
    return info[2] * info[3], info[1]


@contract()
def log_host_overload(db, overload_threshold, hostname,
                      previous_overload, host_mhz, vms_mhz):
    """ Log to the DB whether the host is overloaded.

    :param db: The database object.
     :type db: Database

    :param overload_threshold: The host overload threshold.
     :type overload_threshold: float

    :param hostname: The host name.
     :type hostname: str

    :param previous_overload: Whether the host has been overloaded.
     :type previous_overload: int

    :param host_mhz: The total frequency of the CPU in MHz.
     :type host_mhz: int

    :param vms_mhz: A list of CPU utilization of VMs in MHz.
     :type vms_mhz: list(int)

    :return: Whether the host is overloaded.
     :rtype: int
    """
    overload = overload_threshold * host_mhz < sum(vms_mhz)
    overload_int = int(overload)
    if previous_overload != -1 and previous_overload != overload_int \
            or previous_overload == -1:
        db.insert_host_overload(hostname, overload)
    return overload_int
