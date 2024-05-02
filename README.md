# sysadmin

# Memento / Sheet cheats
|Subject|Link|
|--|--|
|Bash|[MementoBash](https://github.com/crea28/sysadmin/wiki/MementoBash)|
|Docker|[MementoDocker](https://github.com/crea28/sysadmin/wiki/MementoDocker)|
|MySQL|[MementoMySQL](https://github.com/crea28/sysadmin/wiki/MementoMySQL)|
|PostgreSQL|[MementoPostgreSQL](https://github.com/crea28/sysadmin/wiki/MementoPSQL)|
|Tar|[MementoTar](https://github.com/crea28/sysadmin/wiki/MementoTar)|


- **ansible :** contains .yml files can be used for ansible
- **monitoring-scripts :** contains .sh files can be used for nagios/icinga2

## monitoring-scripts

"monitoring-scripts" is a repository about small monitoring scripts for Icinga and Nagios.
It's free to use and modify.

|Script|Description|
|--|--|
|check_github.sh|check the github status|
|check_iptables.sh|check if iptables rules are activated| 
|check_puppetagent.sh|check if puppetagent is running|
|check_redis.sh|check if redis is running and responding with ping-pong command|
|check_ssl_cert.sh|check the status of the ssl certificate (date, expiration)|
|check_url_statuscode.sh|check the status code of URL in using CURL|
|check_if_dead.sh|check when a person is marked as dead on wikipedia (w3m must be installed on the machine)|
|check_galera_cluster.sh|check your galera cluster (cluster_size,cluster_status,cluster_ready,cluster_connected,cluster_local_state,cluster_replication_flow)|
|check_mysql_repl.sh|check the status of a MySQL/MariaDB cluster|
|check_uptime.sh|check the uptime of a linux server. Only check the reboot|
|check_psql_replication_delay.sh|check the delay between master and slave (read-only) postgresql servers|
|check_rbt_queue.sh|check the number of message in specifics rabbitmq queues|
|check_cpu.sh|check the cpu load. Warning end critical tresholds can be modified into the script|


- **scripts :** contains files personnal scripts and files can be used for backups, sysadmin and other stuff

|Script|Description|
|--|--|
|createRabbitMQ.sh|	create/delete/list informations about RabbitMQ instance|
|feed.py|print a RSS feed into term|
|gen_thumb.sh|create a thumb dir ans create a thumb file for all .jpg and .JPG picture|
|save_es.sh|create a dump of elasticsearch indexes|
|save_mongodb.sh|create a dump of all databases|
|save_mysql.sh|create a mysqldump of all databases. You have to create a ~/.my.cnf file or modify the script|
|send_amazon_s3.sh|send_amazon_s3.sh file.tar.gz. Send a file to an Amazon s3 bucket|
|timer.sh| [test] create a timer (minutes/seconds) to send an audio and ubuntu desktop notification|
|watermark.sh|create watermarked picture|
|git-backup.sh|create backup of private and public repositories|

### Security Resources
- [https://www.cisecurity.org/cis-benchmarks](https://www.cisecurity.org/cis-benchmarks)
