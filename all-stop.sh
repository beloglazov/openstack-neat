#!/bin/sh

service openstack-neat-global-manager stop
service openstack-neat-db-cleaner stop
./compute-local-manager-stop.py
./compute-data-collector-stop.py
