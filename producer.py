from os import environ
import models.sensor as sensor
from redis import Redis
from time import sleep

def connect_to_redis():
    hostname = environ.get("REDIS_HOSTNAME", "localhost")
    port = environ.get("REDIS_PORT", 6379)
    r = Redis(hostname, port, retry_on_timeout=True, db=1)
    return r


def produce_datas(redis_connection):
    try:
        redis_connection.xadd('raspberry', sensor.record_datas())
    except ConnectionError as e:
        print("ERROR REDIS CONNECTION: {}".format(e))
    sleep(0.5)


if __name__ == "__main__":
    while True:
        produce_datas(connect_to_redis())
