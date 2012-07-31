#!/bin/sh

pandoc \
    --number-sections \
    --bibliography=bibliography.bib --csl=ieee.csl \
    --output=../openstack-neat-blueprint.epub \
    openstack-neat-blueprint.md
