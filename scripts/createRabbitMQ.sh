#!/bin/bash 
# createRabbitMQ.sh
# Date : 28/01/2015
# Version 2.1

# Colors
RED=$(tput setaf 1)
BOLD=$(tput bold)
RESET=$(tput sgr0)

# Variables


# not root no chocolate
if [ `id -u` -ne 0 ]; then
        echo "You need root privileges to run this script"
        exit 1
fi

function rbtmq_addUser {
	echo -n "Username : "
	read adduser
	
	RABBITMQ_PASS=`/usr/bin/makepasswd --count=1 --chars=12 --crypt-md5 | /usr/bin/awk '{print $1}' `

	rabbitmqctl delete_user $adduser
	rabbitmqctl delete_vhost $adduser
	rabbitmqctl add_user $adduser $RABBITMQ_PASS	
	rabbitmqctl add_vhost $adduser
	rabbitmqctl set_permissions -p $adduser $adduser  ".*" ".*" ".*"
	rabbitmqctl set_user_tags $adduser management

        rabbitmqctl set_policy ha-all "${adduser}.*" '{"ha-mode":"all"}'

	echo "$adduser - $RABBITMQ_PASS"
}

function rbtmq_delUser {
	echo -n "Username : "
	read deluser

	rabbitmqctl delete_user $deluser
	rabbitmqctl delete_vhost $deluser
}

function rbtmq_listUser {
        rabbitmqctl list_users
}

function rbtmq_listVhost {
        rabbitmqctl list_vhosts
}


function help {
        echo "";
        echo "Options:";
        echo "";
        echo "adduser       add RabbitMQ user and vhost";
        echo "deluser 	    remove RabbitMQ user and vhost";
        echo "listuser      users listing";
        echo "listvhost     vhosts listing";
}

# main program
if [ $# != "1" ]; then 
        echo "argument missing" ;
        help;
else
        while (true)
        do
                case $1 in 
                        adduser)
                                rbtmq_addUser;
                                exit 1;
                        ;;
                        deluser)
                                rbtmq_delUser;
                                exit 1;
                        ;;
                        listuser)
                                rbtmq_listUser;
                                exit 1;
                        ;;
                        listvhost)
                                rbtmq_listVhost;
                                exit 1;
                        ;;
                        help)
				help;
				exit 1;
				;;
                        *)
                                help;
                                exit 1;                    
                        ;;
                esac 
        done
fi
