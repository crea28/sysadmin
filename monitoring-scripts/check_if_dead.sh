#!/bin/bash 
# Script : check_if_dead.sh 
# Author : crea28.fr

DATE=$(date "+%d/%m/%y %H:%M:%S")

OUTPUT_OK=("");
OUTPUT_CRIT=("");
OUTPUT_WARN=("");

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

# Wikipedia URL Listing
people=(
	'https://fr.wikipedia.org/wiki/xxx'
	'https://fr.wikipedia.org/wiki/xxx'

);

for star in "${people[@]}"
do
	DEAD=`w3m -dump ${star} | grep "et mort le"`
	WESH=`echo $?`

	if [ "$WESH" == "0" ]; then 
		OUTPUT_CRIT+=($star)
	else 
		OUTPUT_OK+=($star)
	fi
done

if [ "${#OUTPUT_CRIT[@]}" != '1' ]; then
        printf "CRITICAL - R.I.P\n";
        echo "${OUTPUT_CRIT[@]}"                                                                                                                                                                                                             
        exit $STATE_CRITICAL;
else
        printf "OK - They are still here !\n";
        echo "${OUTPUT_OK[@]}";
        exit $STATE_OK;
fi

exit $STATE_UNKNOWN;
