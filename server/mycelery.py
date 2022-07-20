from celery import Celery
from EmojiCloud.canvas import RectangleCanvas, EllipseCanvas, MaskedCanvas
from EmojiCloud.EmojiCloud1 import plot_dense_emoji_cloud
from EmojiCloud.vendors import get_emoji_vendor_path
import os
import io
import json
import asyncio
from settings import *
from myredis import get_redis_instance


app = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)
app.conf.update(
    ask_serializer='pickle',
    accept_content=['pickle', 'json']
)

rd = get_redis_instance()

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


