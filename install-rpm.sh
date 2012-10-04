#!/bin/sh

./build-rpm.sh
yum reinstall -y dist/openstack-neat-0.1-1.noarch.rpm
