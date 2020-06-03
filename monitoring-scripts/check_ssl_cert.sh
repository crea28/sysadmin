#!/bin/bash
# Script : check_ssl_cert.sh
# Author : crea28.fr

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

shopt -s extglob

OUTPUT_OK=("");
OUTPUT_WARN=("");
OUTPUT_CRIT=("");

# URL listing
address=(
		'www.mywebsite1.com'
		'mywebsite2.com'
)

for url in "${address[@]}"
do
	output=$(echo | openssl s_client -connect $url:443 -servername $url 2>/dev/null | openssl x509 -noout -dates)
	start_date=$(echo $output | sed 's/.*notBefore=\(.*\).*not.*/\1/g')
	end_date=$(echo $output | sed 's/.*notAfter=\(.*\)$/\1/g')
	start_epoch=$(date +%s -d "$start_date")
	end_epoch=$(date +%s -d "$end_date")
	epoch_now=$(date +%s)
	seconds_to_expire=$(($end_epoch - $epoch_now))
	days_to_expire=$(($seconds_to_expire / 86400))

	if (( "${end_epoch}" < "${epoch_now}" )); then
		# invalid cert and expired since ${days_to_expire} days
		OUTPUT_CRIT+=(${url})
	elif [[ "${days_to_expire}" -ge 1 && "${days_to_expire}" -le 15 ]]; then 
    		# valid cert but will expire in ${days_to_expire} days
    		OUTPUT_WARN+=(${url})
	elif (( "${end_epoch}" > "${epoch_now}" )); then
		# valid cert and expire in ${days_to_expire} days
		OUTPUT_OK+=(${url})
	fi
done

if [ "${#OUTPUT_CRIT[@]}" != '1' ]; then
 	printf "CRITICAL - URLs\n";
	echo "${OUTPUT_CRIT[@]}"
	echo "${OUTPUT_WARN[@]}"
	exit ${STATE_CRIT};
elif [ "${#OUTPUT_WARN[@]}" != '1' ]; then
	printf "WARNING - URLs\n";
	echo "${OUTPUT_WARN[@]}"
	echo "${OUTPUT_CRIT[@]}"
	exit ${STATE_WARN};
else
	printf "OK - URLs ${OUTPUT[@]}\n";
	echo "${OUTPUT_OK[@]}"
 	exit ${STATE_OK};
fi

exit ${STATE_UNKNOWN};
