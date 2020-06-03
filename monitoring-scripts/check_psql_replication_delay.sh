#!/bin/bash 
# check_psql_replication_delay.sh
# Author : https://github.com/crea28 

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

# Time
# default
TIMEDEFAULT="00:00:00"
TIMEDEFAULT2SEC=`date --date="${TIMEDEFAULT}" +%s`
# psql
TIMEPSQL=`su -c "psql -t -c \"SELECT now() - pg_last_xact_replay_timestamp() AS replication_delay\"" postgres | cut -d "." -f1`
TIMEPSQL2SEC=`date --date="${TIMEPSQL}" +%s`
# limit
TIMELIMIT2SEC="300"

# Delay in seconds
let "DIFF=${TIMEPSQL2SEC}-${TIMEDEFAULT2SEC}"

if [ "${DIFF}" -gt "${TIMELIMIT2SEC}" ]; then
        echo "Replication over than ${TIMELIMIT2SEC} seconds | delay=${DIFF}"
        exit ${STATE_CRITICAL}
else
        echo "Replication less than ${TIMELIMIT2SEC} seconds | delay=${DIFF}"
        exit ${STATE_OK}
fi

exit ${STATE_UNKNOWN}
