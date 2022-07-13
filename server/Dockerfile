FROM python:3.10

WORKDIR /src

RUN pip3 install fastapi 'uvicorn[standard]' Pillow matplotlib numpy pandas 'celery[redis]'

COPY . .

CMD [ 'python3', '-m', "uvicorn", "main:app", "--host 0.0.0.0", "--port 8000", "--reload"]