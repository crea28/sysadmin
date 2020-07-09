#!/bin/bash
# Script : check_github.sh
# https://www.githubstatus.com/api

VERSION="1.2"

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

shopt -s extglob

STATUS_GITHUB=`curl --silent 'https://kctbh9vrtdwd.statuspage.io/api/v2/status.json' | python -mjson.tool | grep "indicator" | awk -F ":" '{print $2}' | sed 's/"//g' | xargs`;

case ${STATUS_GITHUB} in
	none)
		echo "Github is running (status=${STATUS_GITHUB})"
    		exit ${STATE_OK}
		;;
	minor)
		echo "Github seems in trouble (status=${STATUS_GITHUB})"
		exit ${STATE_WARNING}
		;;
	major)
		echo "Github seems in trouble (status=${STATUS_GITHUB})"
		exit ${STATE_WARNING}
		;;
	critical)
		echo "Github is down (status=${STATUS_GITHUB})"
		exit ${STATE_CRITICAL}
		;;
	*)
		echo "Script error"
		exit ${STATE_UNKNOWN}
		;;
esac

exit ${STATE_UNKNOWN}
