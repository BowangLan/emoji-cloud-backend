sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get install -y python3-pip
sudo pip3 install rich Pillow fastapi 'uvicorn[standard]' matplotlib numpy pandas 'celery[redis]'
sudo apt-get install nodejs npm
sudo npm i -g pm2
chmod 777 ./engine_setup.sh && ./engine_setup.sh