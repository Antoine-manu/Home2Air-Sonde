import models.sensor
import redis
from uuid import uuid4
import time
from os import environ
import flask
import json


r = redis.Redis(host='localhost', port=6379, db=1)

stream_key = environ.get("STREAM", "jarless-1")


def connect_to_redis():
    hostname = environ.get("REDIS_HOSTNAME", "localhost")
    port = environ.get("REDIS_PORT", 6379)

    r = redis.Redis(hostname, port, retry_on_timeout=True)
    return r


def get_data():
    stream_data = r.xrange('mystream')
    # read_samples = r.xread({'mystream': b"0-0"})
    # Parse the JSON string back into a list
    print(stream_data[-1])
    models.sensor.record_datas()


while 1:
    get_data()
    # display_all_datas()
    time.sleep(5)
