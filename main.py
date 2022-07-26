from celery.result import AsyncResult
from fastapi import FastAPI, Request, File, UploadFile, WebSocket, HTTPException
from starlette.websockets import WebSocketState
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import uuid
import io
import os
import threading
import time
import redis

from mycelery import process_emoji
from myredis import get_redis_instance
from settings import *
from rich.console import Console

console = Console()


class EmojiCloudTaskManager:

    rd: redis.Redis = None
    RUNNING_TASK_REDIS_KEY = RUNNING_TASK_REDIS_KEY
    FAILED_TASK_REDIS_KEY = FAILED_TASK_REDIS_KEY
    RESULT_KEY = RESULT_KEY
    CANCELLED_TASK_REDIS_KEY = CANCELLED_TASK_REDIS_KEY

    def __init__(self):
        self.rd = get_redis_instance()

    def get_task_result(self, sid: str):
        return self.rd.hget(self.RESULT_KEY, sid)

    def task_success(self, sid: str):
        return self.rd.hexists(self.RESULT_KEY, sid)

    def is_task_cancelled(self, task_id: str):
        return self.rd.sismember(self.CANCELLED_TASK_REDIS_KEY, task_id)

    def has_task_started(self, task_id: str):
        return self.rd.sismember(self.RUNNING_TASK_REDIS_KEY, task_id)

    def add_task_from_started_list(self, task_id: str):
        return self.rd.sadd(self.RUNNING_TASK_REDIS_KEY, task_id)

    def remove_task_from_started_list(self, task_id: str):
        return self.rd.srem(self.RUNNING_TASK_REDIS_KEY, task_id)

    def add_task_to_cancelled_list(self, task_id: str):
        return self.rd.sadd(self.CANCELLED_TASK_REDIS, task_id)

    def remove_task_from_cancelled_list(self, task_id: str):
        return self.rd.srem(self.CANCELLED_TASK_REDIS, task_id)
    
    def get_task_error_msg(self, task_id: str):
        return self.rd.hget(self.FAILED_TASK_REDIS_KEY, task_id)

    def set_task_error_msg(self, task_id: str, msg: str):
        return self.rd.hset(self.FAILED_TASK_REDIS_KEY, task_id, msg)


def get_fastapi_app():
    app = FastAPI()

    if os.environ.get('PRODUCTION') and os.environ.get('PRODUCTION') == 'TRUE':
        origins = []
        if os.environ.get('HOST_IP'):
            origins.append("http://{}".format(HOST_IP))
        if os.environ.get('DOMAIN'):
            origins.append("http://{}".format(DOMAIN))
    else:
        origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:3000",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if not os.path.exists(static_file_dir):
        os.makedirs(static_file_dir)
    app.mount("/static", StaticFiles(directory=static_file_dir), name="static")

    return app



emoji_task_manager = EmojiCloudTaskManager()
app = get_fastapi_app()


@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    localname = os.path.join('static', file.filename)
    while os.path.exists(localname):
        localname += '1'
    with open(localname, 'wb') as f:
        f.write(content)
        return {'status': 200, 'data': {'url': localname}}


@app.get('/result/{sid}')
async def get_result(sid: str):
    result = emoji_task_manager.get_task_result(sid)
    if result != None:
        iterator = io.BytesIO(bytes.fromhex(result.decode()))
        return StreamingResponse(iterator, media_type='image/png')
    else:
        return HTTPException(status_code=404)


class ResultCheckingThread(threading.Thread):

    r: AsyncResult
    sid: str

    def __init__(self, r, websocket: WebSocket, sid: str):
        super(ResultCheckingThread, self).__init__()
        self.r = r
        self.websocket = websocket
        self.sid = sid
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        console.log('start checking')
        while self.r.status == 'PENDING':
            if self._stop.isSet():
                if emoji_task_manager.has_task_started(self.r.id):
                    console.log('stopping running task, task id: {}'.format(self.r.id))
                    self.r.revoke()
                    emoji_task_manager.remove_task_from_started_list(self.r.id)
                else:
                    console.log('cancelling waiting task, task id: {}'.format(self.r.id))
                    emoji_task_manager.add_task_to_cancelled_list(self.r.id)
                return
            pass
        console.log('finish checking')
        async def send():
            if self._stop.isSet():
                return
            if emoji_task_manager.task_success(self.sid):
                try:
                    await self.websocket.send_json({'e': 'ready'})
                    console.log("result ready sent")
                except RuntimeError:
                    console.log("ws already closed")
            else:
                error_msg = emoji_task_manager.get_task_error_msg(self.r.id).decode()
                await self.websocket.send_json({'e': 'error', 'msg': error_msg})
                return
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        loop.run_until_complete(send())



@app.websocket('/plot')
async def plot_ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def parse_json_data(data, t_wrapper):
        if not data.get('e'):
            await websocket.send_json({'err': 'Invalid event', 'status': 401})
            await websocket.close()
            return False
        elif data['e'] == 'exit':
            await websocket.close()
            return False
        elif data['e'] == 'plot':
            console.log('plot')

            sid = str(uuid.uuid4())
            await websocket.send_json({'e': 'sid', 'data': {'sid': sid}})
            r = process_emoji.delay(data['data'], sid)
            th = ResultCheckingThread(r, websocket, sid)
            th.start()
            t_wrapper['th'] = th

        elif data['e'] == 'cancel':
            console.log("cancel plot")
            if t_wrapper.get('th'):
                console.log('task cancelling')
                # t_wrapper['r'].revoke()
                t_wrapper['th'].stop()

        return True

    t_wrapper = {}
    while True:
        console.log("waiting for msg...")
        data = await websocket.receive_json()
        console.log("got msg")
        console.log(data)
        b = await parse_json_data(data, t_wrapper)
        if not b:
            break



@app.get('/emoji/exists')
def emoji_exists(req: Request):
    pass


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, log_level='info',
                reload=True, workers=12)
