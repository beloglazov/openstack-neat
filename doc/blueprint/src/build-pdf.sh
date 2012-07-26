#!/bin/sh

pandoc \
    --smart \
    --table-of-contents \
    --number-sections \
    --output=../openstack-neat-blueprint.pdf \
    openstack-neat-blueprint.md
