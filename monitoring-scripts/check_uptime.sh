#!/bin/bash
# Script : check_uptime.sh
# Author : crea28.fr


# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

UPT=`uptime | grep "day"`
OK=`echo $?` 

	if [ ${OK} == "1" ]; then
		# less than 1 day
		UPT=`awk '{print $0/60;}' /proc/uptime`
		if (( ${UPT%%.*} < 20 )) ; then
			# less than 20min
			echo "CRITICAL - Last reboot : ${UPT} minutes";
			exit ${STATE_CRITICAL};
		else
			echo "WARNING - Last reboot : ${UPT} minutes"
			exit ${STATE_WARNING};
		fi
	else
		UPT=`uptime | awk '{print $3}'`;
		echo "OK - Last reboot since ${UPT} day(s)"
		exit ${STATE_OK}; 
	fi

exit ${STATE_UNKNOWN};
