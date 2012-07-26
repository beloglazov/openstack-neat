#!/bin/sh

python2 setup.py -q test
rm -rf openstack_neat.egg-info
