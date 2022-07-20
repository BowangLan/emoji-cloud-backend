sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get install -y python3-pip
sudo pip3 install rich Pillow 'celery[redis]'
sudo apt-get install nodejs npm
sudo npm i -g pm2
pm2 start "python3 -m celery -A mycelery worker --loglevel=info --without-heartbeat --without-gossip --without-mingle --concurrency 4" --name celery