#!/bin/bash
# check_google_ping.sh

OUTPUT_OK=("");
OUTPUT_CRIT=("");
LOGFILE="chek_google_ping.log"
DATE=`date +%Y-%m-%d\ %H:%M:%S`

ARRAYPING=(
        'www.google.fr' 
);

for client in ${ARRAYPING[@]}
do
        # -W 3 = Timeout 3 seconds
        ping -c 1 ${client} -W 3 > /dev/null

        # check last command
        if [[ `echo $?` != "0" ]]; then
           #Critical
           OUTPUT_CRIT+=(${client})
        else
           #Ok
           OUTPUT_OK+=(${client})
        fi
done

if [ "${#OUTPUT_CRIT[@]}" != '1' ]; then
       echo "${DATE} - Google is not responding" >> "${LOGFILE}";
fi

