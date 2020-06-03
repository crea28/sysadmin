#!/bin/bash 
# Script : check_redis.sh
# Author : crea28.fr

VERSION="1.1"

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

shopt -s extglob

RESULT=`redis-cli ping`

if [ ${RESULT} == "PONG" ]; then
    printf "OK - Redis - ${RESULT} - `date` \n"
    exit ${STATE_OK}
else 
    printf "CRITICAL - Redis - ${RESULT} - `date` \n"
    exit ${STATE_CRITICAL}
fi

exit ${STATE_UNKNOWN}
