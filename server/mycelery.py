from celery import Celery
from EmojiCloud.canvas import RectangleCanvas, EllipseCanvas, MaskedCanvas
from EmojiCloud.EmojiCloud1 import plot_dense_emoji_cloud
from EmojiCloud.vendors import get_emoji_vendor_path
import os
import io
import json
import asyncio
import redis


static_file_dir = 'static'


app = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
app.conf.update(
    ask_serializer='pickle',
    accept_content=['pickle', 'json']
)

rd = redis.Redis(
    host='localhost',
    port=6379,
    db=0
)

@app.task
def process_emoji(data, sid: str):
    print('start processing')
    canvas_type_to_class = {
        'Rectangle': lambda data: RectangleCanvas(h=data['canvas_height'], w=data['canvas_width'], color=data.get('color')),
        'Ellipse': lambda data: EllipseCanvas(h=data['canvas_height'], w=data['canvas_width'], color=data.get('color')),
        'Masked': lambda data: MaskedCanvas(
            img_mask=os.path.join(static_file_dir, data['masked_file']['file']['name']), 
            contour_width=data['canvas_width'], 
            contour_color=tuple(int(c) for c in data['contour_color'].replace(')', '').replace('(', '').replace(' ', '').split(',')), 
            thold_alpha_contour=data['thold_alpha_contour'], 
            thold_alpha_bb=data['thold_alpha_bb'])
    }
    canvas = canvas_type_to_class[data['canvas_type']](data)
    pimg = plot_dense_emoji_cloud(canvas, get_emoji_vendor_path(
        data['emoji_vendor']), json.loads(data['emoji_data'].replace('\'', '"')))
    bData = io.BytesIO()
    pimg.save(bData, format='png')
    print('finish processing')
    emoji_result = bData.getvalue().hex()
    rd.set(sid, emoji_result, ex=300)
    return emoji_result


@app.task
def notify_ready(ws):
    async def send():
        await ws.send_json({'e': 'ready'})
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send())
