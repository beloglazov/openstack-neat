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

"""

from contracts import contract
import sys
import libvirt


def start(iterations):
    for _ in xrange(iterations):
        collect()
    return iterations


def collect():
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
