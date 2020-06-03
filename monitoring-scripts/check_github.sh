#!/bin/bash
# Script : check_github.sh
# Author : crea28.fr

VERSION="1.1"

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

shopt -s extglob

STATUS_GITHUB=`curl --silent 'https://status.github.com/api/status.json' | python -mjson.tool | grep "status" | awk -F ":" '{print $2}' | sed 's/"//g'`;

if [[ `echo ${STATUS_GITHUB}` == "major" ]]; then
    printf "Github.com - CRITICAL"
    printf "Check on https://status.github.com/"
    exit ${STATE_CRITICAL}
fi

if [[ `echo ${STATUS_GITHUB}` == "minor" ]]; then
    printf "Github.com - WARNING"
    printf "Check on https://status.github.com/"
    exit ${STATE_WARNING}
fi

if [ `echo ${STATUS_GITHUB}` == "good" ]; then
    printf "Github.com - OK"
    exit ${STATE_OK}
fi

exit ${STATE_UNKNOWN}
