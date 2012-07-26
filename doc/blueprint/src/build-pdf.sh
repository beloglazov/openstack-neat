#!/bin/sh

pandoc \
    --smart \
    --table-of-contents \
    --number-sections \
    --bibliography=bibliography.bib --csl=ieee.csl \
    --output=../openstack-neat-blueprint.pdf \
    openstack-neat-blueprint.md
