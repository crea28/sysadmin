#!/bin/bash 
# Script : check_url_statuscode.sh
# Author : crea28.fr

DATE=$(date "+%d/%m/%y %H:%M:%S")
OUTPUT_OK=("");
OUTPUT_CRIT=("");
OUTPUT_WARN=("");

shopt -s extglob

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

# URL listing
address=(
	'www.google.com'
	'www.github.com'
)

for url in "${address[@]}"
do
	STATUS_CODE=`curl -o /dev/null --silent --head --connect-timeout 5 --write-out '%{http_code}\n' -k ${url}`;
		
	if [ "${STATUS_CODE}" != "200" ] && [ "${STATUS_CODE}" != "302" ] && [ "${STATUS_CODE}" != "301" ]; then
		OUTPUT_WARN+=(${url} ${STATUS_CODE})
	else 
		OUTPUT_OK+=(${url})
       	fi
done

if [ "${#OUTPUT_WARN[@]}" != '1' ]; then
        printf "WARNING - URLs\n";
	echo "${OUTPUT_WARN[@]}";
	exit ${STATE_WARNING};
else
        printf "OK - URLs ${OUTPUT_OK[@]}\n";
        exit ${STATE_OK};
fi

exit ${STATE_UNKNOWN};
