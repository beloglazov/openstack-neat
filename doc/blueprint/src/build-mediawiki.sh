#!/bin/sh

pandoc \
    --smart \
    --bibliography=bibliography.bib --csl=ieee.csl \
    --write=mediawiki \
    --output=../openstack-neat-blueprint.mediawiki \
    openstack-neat-blueprint.md

sed -i 's/openstack-neat-deployment-diagram.png/https:\/\/github.com\/beloglazov\/openstack-neat\/raw\/master\/doc\/blueprint\/src\/openstack-neat-deployment-diagram.png/g' ../openstack-neat-blueprint.mediawiki
sed -i 's/openstack-neat-local-manager.png/https:\/\/github.com\/beloglazov\/openstack-neat\/raw\/master\/doc\/blueprint\/src\/openstack-neat-local-manager.png/g' ../openstack-neat-blueprint.mediawiki
sed -i 's/openstack-neat-sequence-diagram.png/https:\/\/github.com\/beloglazov\/openstack-neat\/raw\/master\/doc\/blueprint\/src\/openstack-neat-sequence-diagram.png/g' ../openstack-neat-blueprint.mediawiki
