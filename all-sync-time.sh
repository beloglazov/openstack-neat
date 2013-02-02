#!/bin/sh

./compute-sync-time.py
service ntpdate restart
