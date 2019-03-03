import os
import time

from web import celery_app
from web.mongo import Mongo
from .utils import auto_save_result
from celery.contrib import rdb


@celery_app.task
@auto_save_result
def get_block_by_height(height):
    #rdb.set_trace()
    block = Mongo.db(os.environ['MONGODB_NAME']).blocks.find_one({'height': height})
    block['_id'] = ''  # mongo ObjectID is not JSON serializable, and I don't yet have nice solution
    return block


@celery_app.task
@auto_save_result
def wait_n_seconds(seconds):
    #rdb.set_trace()
    time.sleep(seconds)
    return {'result': f'waited {seconds}s'}
