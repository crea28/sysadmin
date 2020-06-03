#!/bin/bash
# save_mysql.sh
#######
# Author : Crea28.fr
# mysqldump of all databases 
# delete older backups
# keep only the backup of the day
# Version 1.1
#######

#######
# Variables
#
HOST=`uname -a | awk  {'print $2'}`
USER=`whoami`
DATE=$(date "+%F")
DEST="" #TO_FILL
REPBACKUP="" #TO_FILL
MAIL="" #TO_FILL
PID_FILE="save_mysql.pid"

function sendemail {
        recipients=$1
        subject=$2
        from=root
        message=$3

/usr/sbin/sendmail -t "$recipients" <<EOF
Subject: $subject
From: $from

$message
EOF
}

# check if script is running
if [ -e ${PID_FILE} ]; then
	sendemail ${MAIL} "`hostname` : save_mysql.sh" "The script still working !"
	exit 1;
else
	echo "$$" > ${PID_FILE}
fi

# check if root rights
if [ ! ${USER} ]; then
	echo "No root, no backup !"
	exit 1;
fi

# delete older backups
rm -rf ${REPBACKUP}/*

# create backup directory
if [ ! -e ${DEST} ]; then
        mkdir -p ${DEST}
        fi

save_mysql() {
	for DB in $(mysql -e "SHOW DATABASES;" -s --skip-column-names | grep -Ev 'information_schema|performance_schema');
	do
		mkdir -p ${DEST}/
		mysqldump --single-transaction --events ${DB} > ${DEST}/${DB}-${DATE}.sql
		gzip "${DEST}/${DB}-${DATE}.sql"
	done
}

save_mysql;

#Garbage
rm ${PID_FILE}

exit 0;
# End of script
