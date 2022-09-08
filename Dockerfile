FROM python:3.10

WORKDIR /src

COPY . .

RUN chmod 777 ./setup.sh && ./setup.sh

CMD [ "pm2 start python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" ]