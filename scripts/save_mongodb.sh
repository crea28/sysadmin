#!/bin/bash 
# Script : save_mongodb.sh
# Author : crea28.fr
# dump all databases in a mongodb server


######
# Variables
#
DATE=$(date "+%F")
REPBACKUP="/my_dir/$DATE"

if [ `id -u` -ne 0 ]; then
        echo "You need root privileges to run this script"
        exit 1
fi

function saveMongo() {
	if [ ! -e $REPBACKUP ]; then
		mkdir -p $REPBACKUP
	else
	        rm -rf $REPBACKUP
		mkdir -p $REPBACKUP
	fi

      	for db in `show dbs | mongo | grep "GB" | awk {'print $1'}`
       	do
              	mongodump --db $db -o $REPBACKUP
		cd $REPBACKUP && tar czf $db.tar.gz $db
		rm -rf $REPBACKUP/$db
       	done
}

saveMongo
