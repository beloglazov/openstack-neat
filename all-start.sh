#!/bin/sh

service openstack-neat-global-manager start
service openstack-neat-global-manager start
./compute-local-manager-start.py
./compute-data-collector-start.py
