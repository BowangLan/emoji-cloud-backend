sudo service redis-server start
sudo service nginx start
cd client
pm2 start "npm run build && npm run start" --name client
cd ../server
pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" --name server
pm2 start "python3 -m celery -A mycelery worker --loglevel=info --autoscale" --name celery
