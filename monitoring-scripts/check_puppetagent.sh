#!/bin/bash
# Script : check_puppetagent.sh
# Author : crea28.fr

VERSION="1.1"

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

shopt -s extglob

if [[ -e "/var/run/puppet/agent.pid" ]]; then
    printf "Puppet Agent - OK"
    exit ${STATE_OK}
else 
   printf "Puppet Agent - CRITICAL - /var/run/puppet/agent.pid doesn't exist"
   exit ${STATE_CRITICAL}
fi

exit ${STATE_UNKNOWN}
