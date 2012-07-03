#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import libvirt
import sys
import time


def getNumberOfPhysicalCpus(connection):
    return connection.getInfo()[2]


def getDomainTotalCpuTime(domain):
    return domain.getCPUStats(True, 0)[0]['cpu_time']


def getCpuUtilization(domain, numberOfPhysicalCpus):
    prevTime = time.time()
    prevCpuTime = getDomainTotalCpuTime(domain)
    time.sleep(1)
    currTime = time.time()
    currCpuTime = getDomainTotalCpuTime(domain)

    print "Prev time: " + str(prevTime)
    print "Prev cpu time: " + str(prevCpuTime)
    print "Curr time: " + str(currTime)
    print "Curr cpu time: " + str(currCpuTime)

    print "CPU utilization: "
    print ((currCpuTime - prevCpuTime) / ((currTime - prevTime) * 1000000000 * numberOfPhysicalCpus))


conn = libvirt.openReadOnly(None)
if conn is None:
    print 'Failed to open connection to the hypervisor'
    sys.exit(1)

try:
    dom0 = conn.lookupByName("cirros")
except:
    print 'Failed to find the main domain'
    sys.exit(1)


numberOfPhysicalCpus = getNumberOfPhysicalCpus(conn)
print "Host CPUs: " + str(numberOfPhysicalCpus)

getCpuUtilization(dom0, numberOfPhysicalCpus)


#print "Domain 0: id %d running %s" % (dom0.ID(), dom0.OSType())
#print dom0.info()
#print dom0.getCPUStats(1, 0)
#print dom0.vcpus()
#print dom0.vcpuPinInfo(0)
#print conn.getCPUStats(1, 0)
