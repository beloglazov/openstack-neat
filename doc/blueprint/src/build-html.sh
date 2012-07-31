#!/bin/sh

pandoc \
    --standalone \
    --smart \
    --self-contained \
    --table-of-contents \
    --number-sections \
    --bibliography=bibliography.bib --csl=ieee.csl \
    --output=../openstack-neat-blueprint.html \
    openstack-neat-blueprint.md
