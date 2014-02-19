#!/bin/bash

echo "Trying to deploy $1..."
fab deploy:commit=$1 --host localhost --user root -i /home/kap10/root_local_key
