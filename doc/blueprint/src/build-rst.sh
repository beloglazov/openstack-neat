#!/bin/sh

pandoc \
    --smart \
    --bibliography=bibliography.bib --csl=ieee.csl \
    --output=../../../README.rst \
    readme-intro.md \
    openstack-neat-blueprint.md

sed -i 's/openstack-neat-deployment-diagram.png/\/beloglazov\/openstack-neat\/raw\/master\/doc\/blueprint\/src\/openstack-neat-deployment-diagram.png/g' ../../../README.rst
sed -i 's/openstack-neat-local-manager.png/\/beloglazov\/openstack-neat\/raw\/master\/doc\/blueprint\/src\/openstack-neat-local-manager.png/g' ../../../README.rst
sed -i 's/openstack-neat-sequence-diagram.png/\/beloglazov\/openstack-neat\/raw\/master\/doc\/blueprint\/src\/openstack-neat-sequence-diagram.png/g' ../../../README.rst
