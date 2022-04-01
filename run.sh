#! /bin/bash

echo "NOTE: use only VagrantBox"

runpash=$(pwd)
cd ./web/html
# echo "## build html ##"
# npm install
# npm run build

cd ..
echo "## start webserver (port:8080) ##"
python3.8 server.py &

cd $runpash
echo "## start openflow proxy ##"
python3.8 ofcapture.py