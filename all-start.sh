#!/bin/sh

./compute-data-collector-start.py
service openstack-neat-global-manager start
service openstack-neat-global-manager start

sleep 2

./compute-local-manager-start.py
