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

from mocktest import *
from pyqcy import *

import os
import shutil
import libvirt

import neat.common as common
import neat.locals.collector as collector
import neat.db_utils as db_utils

import logging
logging.disable(logging.CRITICAL)


class Collector(TestCase):

    @qc(10)
    def start(
            iterations=int_(min=0, max=10),
            time_interval=int_(min=0)
    ):
        with MockTransaction:
            state = {'property': 'value'}
            config = {
                'log_directory': 'dir',
                'log_level': 2,
                'local_data_directory': 'data_dir',
                'data_collector_interval': str(time_interval)}
            paths = [collector.DEFAILT_CONFIG_PATH, collector.CONFIG_PATH]
            fields = collector.REQUIRED_FIELDS
            expect(collector).read_and_validate_config(paths, fields). \
                and_return(config).once()
            expect(common).init_logging('dir', 'data-collector.log', 2).once()
            expect(common).start(collector.init_state,
                                 collector.execute,
                                 config,
                                 time_interval).and_return(state).once()
            assert collector.start() == state

    def test_init_state(self):
        with MockTransaction:
            vir_connection = mock('virConnect')
            expect(libvirt).openReadOnly(None). \
                and_return(vir_connection).once()
            physical_cpus = 13
            expect(common).physical_cpu_count(vir_connection). \
                and_return(physical_cpus).once()
            config = {'sql_connection': 'db',
                      'host_cpu_overload_threshold': '0.95',
                      'host_cpu_usable_by_vms': '0.75',
                      'data_collector_data_length': '5'}

            hostname = 'host1'
            mhz = 13540
            ram = 8192
            expect(vir_connection).getHostname().and_return(hostname).once()
            expect(collector).get_host_characteristics(vir_connection). \
                and_return((mhz, ram)).once()

            db = mock('db')
            expect(collector).init_db('db').and_return(db).once()
            expect(db).update_host(hostname,
                                   int(mhz * 0.75),
                                   physical_cpus,
                                   ram).once()

            state = collector.init_state(config)
            assert state['previous_time'] == 0
            assert isinstance(state['previous_cpu_time'], dict)
            assert state['previous_host_cpu_time_total'] == 0.
            assert state['previous_host_cpu_time_busy'] == 0.
            assert state['previous_overload'] == -1
            assert state['vir_connection'] == vir_connection
            assert state['hostname'] == hostname
            self.assertAlmostEqual(state['host_cpu_overload_threshold'],
                                   0.7125, 3)
            assert state['physical_cpus'] == physical_cpus
            assert state['physical_cpu_mhz'] == mhz
            assert state['physical_core_mhz'] == mhz / physical_cpus
            assert state['db'] == db

    @qc(1)
    def get_previous_vms():
        local_data_directory = os.path.join(
            os.path.dirname(__file__), '..', 'resources', 'vms')
        previous_vms = collector.get_previous_vms(local_data_directory)
        assert 'ec452be0-e5d0-11e1-aff1-0800200c9a66' in previous_vms
        assert 'e615c450-e5d0-11e1-aff1-0800200c9a66' in previous_vms
        assert 'f3e142d0-e5d0-11e1-aff1-0800200c9a66' in previous_vms

    @qc
    def get_current_vms(
        ids=dict_(
            keys=int_(min=0, max=1000),
            values=str_(of='abc123-', min_length=36, max_length=36),
            min_length=0, max_length=10
        )
    ):
        with MockTransaction:
            def init_vm(id):
                vm = mock('vm')
                expect(vm).UUIDString().and_return(ids[id]).once()
                expect(vm).state(0).and_return([id * 13, id]).once()
                return vm

            connection = libvirt.virConnect()
            expect(connection).listDomainsID().and_return(ids.keys()).once()
            if ids:
                expect(connection).lookupByID(any_int) \
                    .and_call(lambda id: init_vm(id))
            expected = dict((v, k * 13) for k, v in ids.items())
            assert collector.get_current_vms(connection) == expected

    @qc
    def get_added_vms(
        x=list_(
            of=str_(of='abc123-', min_length=36, max_length=36),
            min_length=0, max_length=5
        ),
        y=list_(
            of=str_(of='abc123-', min_length=36, max_length=36),
            min_length=0, max_length=5
        )
    ):
        previous_vms = list(x)
        if x:
            x.pop(random.randrange(len(x)))
        x.extend(y)
        assert set(collector.get_added_vms(previous_vms, x)) == set(y)

    @qc
    def get_removed_vms(
        x=list_(
            of=str_(of='abc123-', min_length=36, max_length=36),
            min_length=0, max_length=5
        ),
        y=list_(
            of=str_(of='abc123-', min_length=36, max_length=36),
            min_length=0, max_length=5
        )
    ):
        prev_vms = list(x)
        removed = []
        if x:
            to_remove = random.randrange(len(x))
            for _ in xrange(to_remove):
                removed.append(x.pop(random.randrange(len(x))))
        x.extend(y)
        assert set(collector.get_removed_vms(prev_vms, x)) == set(removed)

    @qc
    def substract_lists(
        x=list_(of=int_(min=0, max=20), max_length=10),
        y=list_(of=int_(min=0, max=20), max_length=10)
    ):
        assert set(collector.substract_lists(x, y)) == \
            set([item for item in x if item not in y])

    @qc(1)
    def cleanup_local_vm_data():
        local_data_directory = os.path.join(
            os.path.dirname(__file__), '..', 'resources', 'vms')
        local_data_directory_tmp = os.path.join(
            local_data_directory, 'tmp')
        shutil.rmtree(local_data_directory_tmp, True)
        os.mkdir(local_data_directory_tmp)
        vm1 = 'ec452be0-e5d0-11e1-aff1-0800200c9a66'
        vm2 = 'e615c450-e5d0-11e1-aff1-0800200c9a66'
        vm3 = 'f3e142d0-e5d0-11e1-aff1-0800200c9a66'

        shutil.copy(os.path.join(local_data_directory, vm1),
                    local_data_directory_tmp)
        shutil.copy(os.path.join(local_data_directory, vm2),
                    local_data_directory_tmp)
        shutil.copy(os.path.join(local_data_directory, vm3),
                    local_data_directory_tmp)

        assert len(os.listdir(local_data_directory_tmp)) == 3
        collector.cleanup_local_vm_data(local_data_directory_tmp,
                                        [vm1, vm2, vm3])
        assert len(os.listdir(local_data_directory_tmp)) == 0

        os.rmdir(local_data_directory_tmp)

    @qc(1)
    def cleanup_all_local_data():
        local_data_directory = os.path.join(
        os.path.dirname(__file__), '..', 'resources', 'vms')
        local_data_directory_tmp = os.path.join(
            local_data_directory, 'tmp')
        local_data_directory_tmp_vms = os.path.join(
            local_data_directory_tmp, 'vms')
        local_data_directory_tmp_host = os.path.join(
            local_data_directory_tmp, 'host')
        shutil.rmtree(local_data_directory_tmp, True)
        os.mkdir(local_data_directory_tmp)
        os.mkdir(local_data_directory_tmp_vms)
        vm1 = 'ec452be0-e5d0-11e1-aff1-0800200c9a66'
        vm2 = 'e615c450-e5d0-11e1-aff1-0800200c9a66'
        vm3 = 'f3e142d0-e5d0-11e1-aff1-0800200c9a66'

        shutil.copy(os.path.join(local_data_directory, vm1),
                    local_data_directory_tmp_vms)
        shutil.copy(os.path.join(local_data_directory, vm2),
                    local_data_directory_tmp_vms)
        shutil.copy(os.path.join(local_data_directory, vm3),
                    local_data_directory_tmp_vms)

        shutil.copyfile(os.path.join(local_data_directory, vm1),
                        local_data_directory_tmp_host)
        assert len(os.listdir(local_data_directory_tmp)) == 2
        assert len(os.listdir(local_data_directory_tmp_vms)) == 3

        collector.cleanup_all_local_data(local_data_directory_tmp)

        assert len(os.listdir(local_data_directory_tmp)) == 1
        assert len(os.listdir(local_data_directory_tmp_vms)) == 0

        shutil.rmtree(local_data_directory_tmp, True)

    @qc
    def fetch_remote_data(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=0, max=3000),
                         min_length=0, max_length=10),
            min_length=0, max_length=3
        ),
        data_length=int_(min=1, max=10)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        if x:
            for uuid, data in x.items():
                result = db.vms.insert().execute(uuid=uuid)
                vm_id = result.inserted_primary_key[0]
                for mhz in data:
                    db.vm_resource_usage.insert().execute(
                        vm_id=vm_id,
                        cpu_mhz=mhz)
                x[uuid] = data[-data_length:]
        assert collector.fetch_remote_data(db, data_length, x.keys()) == x

    @qc
    def write_vm_data_locally(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=list_(of=int_(min=0, max=3000),
                         min_length=0, max_length=10),
            min_length=0, max_length=3
        ),
        data_length=int_(min=0, max=10)
    ):
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'resources', 'vms', 'tmp')
        shutil.rmtree(path, True)
        os.mkdir(path)
        collector.write_vm_data_locally(path, x, data_length)
        files = os.listdir(path)

        result = {}
        for uuid in x.keys():
            file = os.path.join(path, uuid)
            with open(file, 'r') as f:
                result[uuid] = [int(a)
                                for a in f.read().strip().splitlines()]

        shutil.rmtree(path)

        assert set(files) == set(x.keys())
        for uuid, values in x.items():
            if data_length > 0:
                assert result[uuid] == values[-data_length:]
            else:
                assert result[uuid] == []

    @qc
    def append_vm_data_locally(
        x=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=tuple_(list_(of=int_(min=0, max=3000),
                                min_length=0, max_length=10),
                          int_(min=0, max=3000)),
            min_length=0, max_length=3
        ),
        data_length=int_(min=0, max=10)
    ):
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'resources', 'vms', 'tmp')
        shutil.rmtree(path, True)
        os.mkdir(path)
        original_data = {}
        to_append = {}
        after_appending = {}
        for uuid, data in x.items():
            original_data[uuid] = data[0]
            to_append[uuid] = data[1]
            if data_length > 0:
                after_appending[uuid] = list(data[0])
                after_appending[uuid].append(data[1])
                after_appending[uuid] = after_appending[uuid][-data_length:]
            else:
                after_appending[uuid] = []

        collector.write_vm_data_locally(path, original_data, data_length)
        collector.append_vm_data_locally(path, to_append, data_length)

        files = os.listdir(path)

        result = {}
        for uuid in x.keys():
            file = os.path.join(path, uuid)
            with open(file, 'r') as f:
                result[uuid] = [int(a)
                                for a in f.read().strip().splitlines()]

        shutil.rmtree(path)

        assert set(files) == set(x.keys())
        for uuid in x.keys():
            assert result[uuid] == after_appending[uuid]

    @qc(10)
    def append_vm_data_remotely(
        vms=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=tuple_(int_(min=1, max=3000),
                          list_(of=int_(min=1, max=3000),
                                min_length=0, max_length=10)),
            min_length=0, max_length=5
        )
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        initial_data = []
        data_to_submit = {}
        final_data = {}

        for uuid, data in vms.items():
            vm_id = db.select_vm_id(uuid)
            data_to_submit[uuid] = data[0]
            final_data[uuid] = list(data[1])
            final_data[uuid].append(data[0])
            for cpu_mhz in data[1]:
                initial_data.append({'vm_id': vm_id,
                                     'cpu_mhz': cpu_mhz})
        if initial_data:
            db.vm_resource_usage.insert().execute(initial_data)

        collector.append_vm_data_remotely(db, data_to_submit)

        for uuid, data in final_data.items():
            assert db.select_cpu_mhz_for_vm(uuid, 11) == data

    @qc
    def append_host_data_locally(
        data=list_(of=int_(min=0, max=3000),
                   min_length=0, max_length=10),
        x=int_(min=0, max=3000),
        data_length=int_(min=0, max=10)
    ):
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'resources', 'host')
        with open(path, 'w') as f:
            f.write('\n'.join([str(x)
                               for x in data]) + '\n')
        collector.append_host_data_locally(path, x, data_length)
        if data_length > 0:
            data.append(x)
            expected = data[-data_length:]
        else:
            expected = []

        with open(path, 'r') as f:
            actual = [int(x)
                      for x in f.read().strip().splitlines()]
        os.remove(path)
        assert actual == expected

    @qc(10)
    def append_host_data_remotely(
        hostname=str_(of='abc123', min_length=5, max_length=10),
        cpu_mhz=int_(min=0, max=3000)
    ):
        db = db_utils.init_db('sqlite:///:memory:')
        db.update_host(hostname, 1, 1, 1)
        collector.append_host_data_remotely(db, hostname, cpu_mhz)
        assert db.select_cpu_mhz_for_host(hostname, 1) == [cpu_mhz]

    @qc
    def get_cpu_mhz(
        cpus=int_(min=1, max=8),
        current_time=float_(min=100, max=1000),
        time_period=float_(min=1, max=100),
        vm_data=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=two(of=int_(min=1, max=100)),
            min_length=0, max_length=10
        ),
        added_vms=dict_(
            keys=str_(of='abc123-', min_length=36, max_length=36),
            values=tuple_(int_(min=1, max=100),
                          list_(of=int_(min=1, max=3000),
                                min_length=0, max_length=10)),
            min_length=0, max_length=5
        )
    ):
        with MockTransaction:
            def mock_get_cpu_time(vir_connection, uuid):
                if uuid in original_vm_data:
                    return original_vm_data[uuid][0] + \
                           original_vm_data[uuid][1]
                else:
                    return added_vms[uuid][0]

            original_vm_data = dict(vm_data)
            previous_time = current_time - time_period
            connection = libvirt.virConnect()
            when(collector).get_cpu_time(connection, any_string). \
                then_call(mock_get_cpu_time)

            previous_cpu_time = {}
            cpu_mhz = {}
            for uuid, data in vm_data.items():
                previous_cpu_time[uuid] = data[0]

            if vm_data:
                to_remove = random.randrange(len(vm_data))
                for _ in xrange(to_remove):
                    tmp = random.choice(vm_data.keys())
                    del vm_data[tmp]
            vms = vm_data.keys()

            current_cpu_time = {}
            for uuid in vms:
                current_cpu_time[uuid] = vm_data[uuid][0] + vm_data[uuid][1]
                cpu_mhz[uuid] = collector.calculate_cpu_mhz(
                    cpus, previous_time, current_time,
                    vm_data[uuid][0], vm_data[uuid][0] + vm_data[uuid][1])

            added_vm_data = {}
            if added_vms:
                for uuid, data in added_vms.items():
                    current_cpu_time[uuid] = data[0]
                    added_vm_data[uuid] = data[1]
                    if data[1]:
                        cpu_mhz[uuid] = data[1][-1]

            vms.extend(added_vms.keys())

            result = collector.get_cpu_mhz(
                connection, cpus, previous_cpu_time,
                previous_time, current_time, vms,
                {}, added_vm_data)

            assert result[0] == current_cpu_time
            assert result[1] == cpu_mhz

    @qc(10)
    def get_cpu_time(
        uuid=str_(of='abc123-', min_length=36, max_length=36),
        x=int_(min=0)
    ):
        with MockTransaction:
            connection = libvirt.virConnect()
            domain = mock('domain')
            expect(connection).lookupByUUIDString(uuid). \
                and_return(domain).once()
            expect(domain).getCPUStats(True, 0). \
                and_return([{'cpu_time': x}]).once()
            assert collector.get_cpu_time(connection, uuid) == x

    @qc
    def calculate_cpu_mhz(
        current_time=float_(min=100, max=1000),
        time_period=float_(min=1, max=100),
        current_cpu_time=int_(min=100),
        cpu_time=int_(min=0, max=100),
        mhz=int_(min=1, max=3000)
    ):
        previous_time = current_time - time_period
        previous_cpu_time = current_cpu_time - cpu_time
        assert collector. \
            calculate_cpu_mhz(mhz, previous_time, current_time,
                              previous_cpu_time, current_cpu_time) == \
            int((mhz * cpu_time / (time_period * 1000000000)))

    @qc
    def get_host_cpu_mhz(
        cpu_mhz=int_(min=1, max=1000),
        prev_total=float_(min=100, max=1000),
        prev_busy=float_(min=1, max=100),
        diff_total=float_(min=100, max=1000),
        diff_busy=float_(min=1, max=100)
    ):
        with MockTransaction:
            total = prev_total + diff_total
            busy = prev_busy + diff_busy
            expect(collector).get_host_cpu_time(). \
                and_return((total, busy)).once()
            assert collector.get_host_cpu_mhz(cpu_mhz, prev_total, prev_busy) == \
                (total,
                 busy,
                 int(cpu_mhz * diff_busy / diff_total))

    @qc(1)
    def get_host_cpu_mhz_exception():
        cpu_mhz = 1
        total = 1.
        prev_total = 0.
        busy = 1.
        prev_busy = 2.
        with MockTransaction:
            expect(collector).get_host_cpu_time(). \
                and_return((total, busy)).once()
            try:
                collector.get_host_cpu_mhz(cpu_mhz, prev_total, prev_busy)
                assert False
            except ValueError:
                assert True

    @qc(10)
    def get_host_cpu_time(
        x=list_(of=int_(min=1, max=1000), min_length=7, max_length=7)
    ):
        with MockTransaction:
            context = mock('context')
            f = mock('file')
            expect(context).__enter__().and_return(f).once()
            when(context).__exit__.and_return(True)
            expect(collector).open('/proc/stat', 'r').and_return(context).once()
            expect(f).readline().and_return(
                '1 ' + ' '.join([str(v) for v in x]) + ' 2 3').once()
            assert collector.get_host_cpu_time() == (float(sum(x)),
                                                     float(sum(x[0:3])))

    @qc(10)
    def get_host_characteristics(
        ram=int_(min=1, max=4000),
        cores=int_(min=1, max=8),
        mhz=int_(min=1, max=3000)
    ):
        with MockTransaction:
            connection = libvirt.virConnect()
            expect(connection).getInfo().and_return(
                ['x86_64', ram, cores, mhz, 1, 1, 4, 2]).once()
            assert collector.get_host_characteristics(connection) == \
                (cores * mhz, ram)

    @qc(1)
    def log_host_overload():
        db = db_utils.init_db('sqlite:///:memory:')
        with MockTransaction:
            expect(db).insert_host_overload('host', 1).once()
            assert collector.log_host_overload(db, 0.9, 'host', -1, 3000, 2800)
        with MockTransaction:
            expect(db).insert_host_overload('host', 0).once()
            assert not collector.log_host_overload(db, 0.9, 'host', -1, 3000, 2600)

        with MockTransaction:
            expect(db).insert_host_overload('host', 1).once()
            assert collector.log_host_overload(db, 0.9, 'host', 0, 3000, 2800)
        with MockTransaction:
            expect(db).insert_host_overload('host', 0).once()
            assert not collector.log_host_overload(db, 0.9, 'host', 1, 3000, 2600)

        with MockTransaction:
            expect(db).insert_host_overload.never()
            assert collector.log_host_overload(db, 0.9, 'host', 1, 3000, 2800)
        with MockTransaction:
            expect(db).insert_host_overload.never()
            assert not collector.log_host_overload(db, 0.9, 'host', 0, 3000, 2600)


def deque_maxlen(coll):
    return int(re.sub("\)$", "", re.sub(".*=", "", coll.__repr__())))
