#!/bin/sh

./compute-update.py

git pull
python setup.py install
