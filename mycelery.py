from celery import Celery
from EmojiCloud.canvas import RectangleCanvas, EllipseCanvas, MaskedCanvas
from EmojiCloud.EmojiCloud import plot_dense_emoji_cloud
from EmojiCloud.vendors import get_emoji_vendor_path
from rich.console import Console
import os
import io
import json
from settings import *
from myredis import get_redis_instance


console = Console()
app = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)
app.conf.update(
    ask_serializer='pickle',
    accept_content=['pickle', 'json']
)

rd = get_redis_instance()

canvas_type_to_class = {
    'Rectangle': lambda data: RectangleCanvas(h=data['canvas_height'], w=data['canvas_width'], color=data.get('color')),
    'Ellipse': lambda data: EllipseCanvas(h=data['canvas_height'], w=data['canvas_width'], color=data.get('color')),
    'Masked': lambda data: MaskedCanvas(
        img_mask=os.path.join(
            static_file_dir, data['masked_file']['file']['name']),
        contour_width=data['canvas_width'],
        contour_color=tuple(int(c) for c in data['contour_color'].replace(
            ')', '').replace('(', '').replace(' ', '').split(',')),
        thold_alpha_contour=data['thold_alpha_contour'],
        thold_alpha_bb=data['thold_alpha_bb'])
}


@app.task(bind=True)
def process_emoji(self, data, sid: str):
    global console
    cancel = rd.sismember(CANCELLED_TASK_REDIS_KEY, self.request.id)
    if cancel == 1:
        console.log('cancel task {}, sid: {}'.format(self.request.id, sid))
        rd.srem(CANCELLED_TASK_REDIS_KEY, self.request.id)
        return
    rd.sadd(RUNNING_TASK_REDIS_KEY, self.request.id)
    console.log('start processing... task id: {}'.format(self.request.id))
    try:
        canvas = canvas_type_to_class[data['canvas_type']](data)
        pimg = plot_dense_emoji_cloud(canvas, get_emoji_vendor_path(
            data['emoji_vendor']), json.loads(data['emoji_data'].replace('\'', '"')))
        bData = io.BytesIO()
        pimg.save(bData, format='png')
        console.log('finish processing')
        emoji_result = bData.getvalue().hex()
        rd.hset(RESULT_KEY, sid, emoji_result)

    except Exception as e:
        rd.hset(FAILED_TASK_REDIS_KEY, self.request.id, str(e))
        console.print('[red1 bold]Process error: [not bold italic bright_red]' + str(e))

    finally:
        rd.srem(RUNNING_TASK_REDIS_KEY, self.request.id)

