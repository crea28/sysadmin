#!/bin/bash
# Script : check_galera_cluster.sh 
# Author : crea28.fr
# http://galeracluster.com/documentation-webpages/monitoringthecluster.html

ST_OK=0
ST_WR=1
ST_CR=2
ST_UK=3

# default values
# can be replaced in using grep with .my.cnf
port=''
mysqlhost=''
mysqluser=''
mysqlpassword=''

function cluster_size() {
	node='3'
	r1=$(mysql -h$mysqlhost -P$port -u$mysqluser -p$mysqlpassword -B -N -e "show status like 'wsrep_cluster_size'"|cut -f 2)

	if [ $r1 -eq $node ]; then
  		echo "OK: number of NODES = $r1"
		exit $ST_OK;
	elif [ $r1 -ne $node ]; then
		echo "CRITICAL: number of NODES = $r1";
		echo "Configuration indicates $node nodes"
		exit $ST_CR;
	else
		exit $ST_UK;
	fi

}

function cluster_status() {
	status="Primary"
	r2=$(mysql -h$mysqlhost -P$port -u$mysqluser -p$mysqlpassword -B -N -e "show status like 'wsrep_cluster_status'"|cut -f 2) 

	if [ "$r2" != 'Primary' ]; then
		echo "CRITICAL: node is not primary"
		exit $ST_CR;
	else
	    	echo "OK : `hostname` is Primary"
		exit $ST_OK;
	fi

}

function cluster_ready() {
	# Value (ON | OFF)
	r4=$(mysql -h$mysqlhost -P$port -u$mysqluser -p$mysqlpassword -B -N -e "show status like 'wsrep_ready'"|cut -f 2) 

	if [ "$r4" != 'ON' ]; then
		echo "CRITICAL: node is not ready"
		exit $ST_CR;
	else
	    	echo "OK: I can accept write-sets from the cluster"
		exit $ST_OK;
	fi
}

function cluster_connected() {
	# Value (ON | OFF)
	r5=$(mysql -h$mysqlhost -P$port -u$mysqluser -p$mysqlpassword -B -N -e "show status like 'wsrep_connected'"|cut -f 2)

	if [ "$r5" != 'ON' ]; then
                echo "CRITICAL: Where is Brian ?"
                exit $ST_CR;
        else
                echo "OK: Network connection is good !"
                exit $ST_OK;
        fi
}

function cluster_local_state() {
	# Synced is the state by default
	r6=$(mysql -h$mysqlhost -P$port -u$mysqluser -p$mysqlpassword -B -N -e "show status like 'wsrep_local_state_comment'"|cut -f 2)
	
	if [ "$r6" != 'Synced' ]; then
		echo "CRITICAL: node is not synced"
		exit $ST_CR;
	else
	        echo "OK: node is synced (Status : $r6)"
		exit $ST_OK;
	fi
}

function cluster_replication_flow() {
	# wsrep_flow_control_paused shows the fraction of the time, since the status variable was last called, that the node paused due to Flow Control
	fcp='0.1';
	r3=$(mysql -h$mysqlhost -P$port -u$mysqluser -p$mysqlpassword -B -N -e "show status like 'wsrep_flow_control_paused'"|cut -f 2) 

	if [ -z "$r3" ]; then
		echo "UNKNOWN: wsrep_flow_control_paused is empty"
		exit $ST_UK ;
	fi

	if [ $(echo "$r3 > $fcp" | bc) = 1 ]; then
		echo "CRITICAL: wsrep_flow_control_paused is > $fcp"
		exit $ST_CR;
	else 
	    	echo "OK: wsrep_flow_control_paused is < $fcp"
		exit $ST_OK;
	fi
}

function help() {
        echo "";
        echo "Options:";
        echo "";
        echo "cluster_size      	Shows the number of nodes in the cluster";
	echo "cluster_status		Shows the primary status of the cluster component";
	echo "cluster_ready		Shows if node can accept queries or not";
	echo "cluster_connected		Shows the network connectivity with any other nodes":
	echo "cluster_local_state	Shows the node state in a human readable format";
	echo "cluster_replication_flow	Shows time since the status variable was last called";
	exit $ST_UK;
}

# main program
if [ $# != "1" ]; then 
        echo "argument missing" ;
        help;
else
        while (true)
        do
                case $1 in 
                        cluster_size)
                                cluster_size;
                                exit 1;
                        	;;
		 	cluster_status)
				cluster_status;
				exit 1;
				;;
			cluster_ready)
			    	cluster_ready;
				exit 1;
				;;
			cluster_connected)
			    	cluster_connected;
				exit 1;
				;;
			cluster_local_state)
			    	cluster_local_state;
				exit 1;
				;;
			cluster_replication_flow)
			    	cluster_replication_flow;
				exit 1;
				;;
			*)
                                help;
                                exit 1;                    
                        ;;
                esac 
        done
fi
