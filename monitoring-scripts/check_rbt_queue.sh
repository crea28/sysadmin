#!/bin/bash

#set -xv 

VERSION="1.2"
LIMIT_RBTMQ_CRITICAL="100"
LIMIT_RBTMQ_WARNING="50"
TMP_FILE="/tmp/rbt_msg.txt"

DATE=$(date "+%d/%m/%y %H:%M:%S")

OUTPUT_OK=("");
OUTPUT_CRIT=("");
OUTPUT_WARN=("");

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

queues=(
    'queue1'
    'queue2'
);

#### Functions ####

# Print version information
print_version()
{
	printf "\n\n$0 - $VERSION\n"
}

### MAIN ###

if [ $# = "0" ]; then 
        echo "argument missing" ;
        exit $STATE_UNKNOWN;
fi

sudo /usr/sbin/rabbitmqctl list_queues -p $1 | grep -v "Listing" > $TMP_FILE

for queue_name in "${queues[@]}"
    do  
        NB_MSG=$(grep ${queue_name} ${TMP_FILE} | awk '{print $2}' | uniq)

        if [[ -z $NB_MSG ]]; then 
            NB_MSG="1";
        fi

        if [[ $NB_MSG == "0" ]]; then 
            NB_MSG="0";
        fi 

        if [ "${NB_MSG}" -ge "${LIMIT_RBTMQ_CRITICAL}" ]; then
                OUTPUT_CRIT+=(${queue_name} ${NB_MSG})
        elif [ "${NB_MSG}" -ge "${LIMIT_RBTMQ_WARNING}" ]; then
                OUTPUT_WARN+=(${queue_name} ${NB_MSG})
        else 
            OUTPUT_OK+=(${queue_name})
        fi
    done

if [ "${#OUTPUT_CRIT[@]}" != '1' ]; then
        printf "CRITICAL - RABBITMQ QUEUES\n";
        echo "${OUTPUT_CRIT[@]}"                                                                                                                                                                                                             
        exit $STATE_CRITICAL;
elif [ "${#OUTPUT_WARN[@]}" != '1' ]; then
        printf "WARNING - RABBITMQ QUEUES\n";
        echo "${OUTPUT_WARN[@]}"                                                                                                                                                                                                             
        exit $STATE_WARN;
else
        printf "OK - RABBITMQ QUEUES\n";
        printf "${OUTPUT_OK[@]}\n";
        exit $STATE_OK;
fi

exit $STATE_UNKNOWN
