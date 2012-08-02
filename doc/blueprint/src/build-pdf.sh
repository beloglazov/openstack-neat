#!/bin/sh

pandoc \
    --smart \
    --table-of-contents \
    --number-sections \
    --template=template.tex \
    --variable=affilation:"`cat affiliation.tex`" \
    --variable=thanks:"`cat thanks.tex`" \
    --bibliography=bibliography.bib --csl=ieee.csl \
    --output=../openstack-neat-blueprint.pdf \
    openstack-neat-blueprint.md
