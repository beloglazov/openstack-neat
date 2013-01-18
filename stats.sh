#!/bin/sh

if [ $# -ne 2 ]
then
    echo "You must specify 2 arguments: start and end time as YYYY-MM-DD HH:MM:SS"
    exit 1
fi

./utils/overload-time-fraction.py root $MYSQL_ROOT_PASSWORD "$1" "$2"
./utils/idle-time-fraction.py root $MYSQL_ROOT_PASSWORD "$1" "$2"
./utils/vm-migrations.py root $MYSQL_ROOT_PASSWORD "$1" "$2"
