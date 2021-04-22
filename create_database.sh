#!/bin/bash

sudo python edit_conf.py

# run build_graph.py and copy the csv's:
python build_graph.py

sudo cp ./keywords.csv /var/lib/neo4j/import/
sudo cp ./urls.csv /var/lib/neo4j/import/
sudo cp ./url2keyword.csv /var/lib/neo4j/import/

# install apoc lib
sudo cp /var/lib/neo4j/labs/apoc-4.2.0.1-core.jar /var/lib/neo4j/plugins/
sudo chown neo4j:adm /var/lib/neo4j/plugins/apoc-4.2.0.1-core.jar
sudo chmod 755 /var/lib/neo4j/plugins/apoc-4.2.0.1-core.jar

sudo neo4j start

# first time you run the script, password is neo4j, so run cypher-shell -u neo4j -p neo4j
# you'll be asked to change the password
# use the new password from then on

cypher-shell -u neo4j -p shekhor --file setup_database.cql --database neo4j