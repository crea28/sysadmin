#!/bin/bash
# Script : check_iptables.sh
# Author : crea28.fr

# /etc/sudoers.d/90-monitoring : 
# # User rules for nagios
# nagios ALL=(root) NOPASSWD:/usr/lib/nagios/plugins/check_iptables.sh

VERSION="1.1"

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

shopt -s extglob

### MAIN ###

STATUS_IPT=`iptables -L -nv | grep "policy ACCEPT" | wc -l` ;


if [[ `echo ${STATUS_IPT}` == "0" ]]; then
    printf "Firewall - OK"
    exit ${STATE_OK}
else 
   printf "Firewall - CRITICAL"
   exit ${STATE_CRITICAL}
fi

exit ${STATE_UNKNOWN}
