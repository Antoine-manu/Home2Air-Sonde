from os import environ
import models.sensor as sensor
from redis import Redis
from uuid import uuid4
from time import sleep

stream_key = environ.get("STREAM", "jarless-1")
producer = environ.get("PRODUCER", "user-1")


def connect_to_redis():
    hostname = environ.get("REDIS_HOSTNAME", "localhost")
    port = environ.get("REDIS_PORT", 6379)

    r = Redis(hostname, port, retry_on_timeout=True)
    return r


# def send_data(redis_connection):
#     try:
#         datas = models.sensor.record_datas()
#         for data in datas:
#             results = {
#                 "temperature": data.temperature,
#                 "pressure": data.pressure,
#                 "humidity": data.humidity,
#                 "light": data.light,
#                 "reduced": data.reduced,
#                 "oxidised": data.oxidised,
#                 "ammoniac": data.nh3
#             }
#             resp = redis_connection.xadd(stream_key, results)
#             print(resp)

#     except ConnectionError as e:
#         print("ERROR REDIS CONNECTION: {}".format(e))

#     sleep(0.5)


# if __name__ == "__main__":
#     connection = connect_to_redis()
#     send_data(connection)
