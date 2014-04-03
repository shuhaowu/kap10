#!/bin/bash

echo "Trying to deploy $1..."
cd /home/kap10/app
source /home/kap10/venv/bin/activate && fab deploy:commit=$1,run=True --host localhost --user root -i /home/kap10/root_local_key
