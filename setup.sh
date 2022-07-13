sudo apt update && sudo apt upgrade
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get install -y python3.9 python3-pip python3-venv nodejs npm nginx redis-server
sudo npm i -g pm2

cd client
npm install
cd ..

cd server
pip3 install fastapi 'uvicorn[standard]' Pillow matplotlib numpy pandas 'celery[redis]'
cd ..

python3 setup.py