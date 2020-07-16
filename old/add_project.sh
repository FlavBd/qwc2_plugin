#!/bin/bash +xv

add_project() {
    echo "Copie $1 dans $server:/opt/qgis-server"
	scp $1 $server:/opt/qgis-server/
	ssh $server 'cd /opt/qwc2/ && python3 ./configqwc2.py'
	ssh $server 'cp /opt/qwc2/themes.json /var/www/html'
	ssh $server 'cp -r /opt/qwc2/assets/img/* /var/www/html/assets/img/'
}

#Chemin où on veut mettre le projet .qgs sur le serveur
project=$(basename $1)
filename=/opt/qgis-server/$project

# Serveur
server='qgisserver@'$2 

if ssh $server test -f $filename
then
    read -p "Le projet existe déjà. Voulez-vous le remplacer (O/N)? " response
    if [[ "$response" =~ ^[YyOo]$ ]]
    then
        echo "Projet remplacé";
        add_project $1;
    else
        echo "Opération annulée";
    fi	
else
	add_project $1
fi