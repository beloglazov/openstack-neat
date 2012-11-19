#!/bin/sh

service openstack-neat-global-manager stop
service openstack-neat-global-manager stop
./compute-local-manager-stop.py
./compute-data-collector-stop.py
