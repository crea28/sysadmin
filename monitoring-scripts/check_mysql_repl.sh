#!/bin/bash 
# Script : check_mysql_repl.sh
# Author : crea28.fr
# /root/.my.cnf must be configured

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

IORUNNING=`mysql -e "SHOW SLAVE STATUS\G" | grep "Slave_IO_Running" | awk '{print $2}'`
SLAVERUNNING=`mysql -e "SHOW SLAVE STATUS\G" | grep "Slave_SQL_Running" | awk '{print $2}'`
SECONDS=`mysql -e "SHOW SLAVE STATUS\G" | grep "Seconds_Behind_Master" | awk '{print $2}'`
LATENCYLIMIT="60"

# to check : Seconds_Behind_Master
if [ $IORUNNING != Yes ] || [ $SLAVERUNNING != Yes ]; then
	# Failed
        echo "MySQL Replication : Failed" 
        exit $STATE_CRITICAL;
elif [ -z $IORUNNING ] || [ -z $SLAVERUNNING ]; then
	# not set
        echo "MySQL Replication : not set"
        exit $STATE_UNKNOWN;
else
	# OK
	if [ "$SECONDS" -gt "$LATENCYLIMIT" ]; then
		#OK
		echo "MySQL Replication : OK"
	        exit $STATE_OK;
	else 
		#Warning
		echo "MySQL Replication : Latency of ${SECONDS} second(s)"
		exit $STATE_WARNING;
	fi
fi

exit $STATE_UNKNOWN;
