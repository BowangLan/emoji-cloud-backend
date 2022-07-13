from fastapi import FastAPI, Request, File, UploadFile, WebSocket, Response, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import redis
import uuid
import io
import os
import threading

from mycelery import process_emoji, notify_ready


static_file_dir = 'static'

rd = redis.Redis(
    host='localhost',
    port=6379,
    db=0
)

app = FastAPI()

if os.environ.get('PRODUCTION') and os.environ.get('PRODUCTION') == 'TRUE':
    origins = []
    if os.environ.get('HOST_IP'):
        origins.append("http://{}".format(os.environ.get('HOST_IP')))
    if os.environ.get('DOMAIN'):
        origins.append("http://{}".format(os.environ.get('DOMAIN')))
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



app.mount("/static", StaticFiles(directory=static_file_dir), name="static")


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
    r = rd.get(sid)
    print(r[:30], type(r))
    iterator = io.BytesIO(bytes.fromhex(r.decode()))
    return StreamingResponse(iterator, media_type='image/png')


@app.websocket('/plot')
async def plot_ws_endpoint(websocket: WebSocket, background_tasks: BackgroundTasks):
    await websocket.accept()
    t_wrapper = {}
    async def parse_json_data(data):
        if not data.get('e'):
            await websocket.send_json({'err': 'Invalid event', 'status': 401})
            await websocket.close()
            return False
        elif data['e'] == 'exit':
            await websocket.close()
            return False
        elif data['e'] == 'plot':
            print('plot')
            # plot data here
            print(data['data'])
            # background_tasks.add_task(process, websocket, data['data'])
            # t = asyncio.create_task(process(websocket, data['data']))
            # t_wrapper['t'] = t

            if data.get('sid') and rd.get(data['sid']):
                await websocket.send_json({'e': 'ready'})
            else:
                sid = str(uuid.uuid4())
                await websocket.send_json({'e': 'sid', 'data': {'sid': sid}})
                r = process_emoji.delay(data['data'], sid)
                print('r')
                print(r, type(r))
                def ch():
                    print('start checking')
                    while r.status == 'PENDING':
                        pass
                    print('finish checking', r.status)
                    print(r.get())
                    async def send():
                        print("start send ready")
                        await websocket.send_json({'e': 'ready'})
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        print("create new event loop")
                        loop = asyncio.new_event_loop()
                    loop.run_until_complete(send())
                th = threading.Thread(target=ch)
                th.start()

        elif data['e'] == 'cancel':
            print("cancel plot")
            # if t_wrapper.get('t'):
            #     print('task cancelling')
            #     t_wrapper['t'].cancel()

        return True

    while True:
        data = await websocket.receive_json()
        b = await parse_json_data(data)
        if not b:
            break


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, log_level='info', reload=True, workers=12)
