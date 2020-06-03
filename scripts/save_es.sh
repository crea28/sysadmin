#!/bin/bash 
# save_es.sh
# backup for elasticsearch 
# to clean all backup : 
# curl -XDELETE 'http://localhost:9200/_snapshot/backup*'

DIR_BACKUP="/var/lib/elasticsearch/backup"
DATE=$(date "+%F");
RANDOM=`od -vAn -N4 -tu4 < /dev/urandom`

if [ `id -u` -ne 0 ]; then
     echo "You need root privileges to run this script"
     exit 1
fi

#echo "delete backup directory"
rm -rf $DIR_BACKUP-$DATE


if [ ! -e $DIR_BACKUP-$DATE ]; then 
	mkdir -p $DIR_BACKUP/$DATE

	echo "Clean all backups"
        curl -XDELETE 'http://localhost:9200/_snapshot/backup/'

	sleep 1;

	echo "create backup"
	curl -XPUT 'http://localhost:9200/_snapshot/backup' -d '{ "type": "fs", "settings": {"location": "'${DIR_BACKUP}/${DATE}'","compress": true}}'

	sleep 1 ; 

	echo "backuping"
	curl -XPUT 'localhost:9200/_snapshot/backup/snapshot_'${DATE}'?wait_for_completion=true'

	# restore
	#curl -XPOST "localhost:9200/_snapshot/backup_$DATE/snapshot/_restore?wait_for_completion=true"

	chown -R elasticsearch.elasticsearch $DIR_BACKUP
	
else
  	echo "Can't create $DIR_BACKUP/$DATE"
fi

