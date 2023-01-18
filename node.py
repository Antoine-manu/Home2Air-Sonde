import subprocess
import redis
import psutil
import os
from flask import Flask, jsonify
app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, db=1)


def kill_producer():
    for process in psutil.process_iter():
        try:
            if process.name() == "python" and "producer.py" in process.cmdline():
                os.kill(process.pid, 9)
                print(f"Successfully killed the producer")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


@app.route('/datas/kill', methods=['GET'])
def kill():
    if kill_producer():
        return jsonify("Fait")
    else:
        return jsonify("Pas fait")


@app.route('/datas', methods=['GET'])
def send_last_five_minutes():
    # kill_producer()
    return jsonify(r.xrange('raspberry', '-', count=5))


@app.route('/datas/minutes/<min>', methods=['GET'])
def send_minutes(min):
    kill_producer()
    if isinstance(min, int):
        return jsonify(r.xrange('raspberry', '-', count=min))


@app.route('/datas/hour', methods=['GET'])
def send_last_hour():
    kill_producer()
    return jsonify(r.xrange('raspberry', '-', count=60))


@app.route('/datas/hour/<h>', methods=['GET'])
def send_hours(h):
    kill_producer()
    if isinstance(h, int):
        return jsonify(r.xrange('raspberry', '-', count=60 * h))


@app.route('/datas/day', methods=['GET'])
def send_last_day():
    kill_producer()
    return jsonify(r.xrange('raspberry', '-', count=1440))


@app.route('/datas/day/<d>', methods=['GET'])
def send_days(d):
    kill_producer()
    if isinstance(d, int):
        return jsonify(r.xrange('raspberry', '-', count=1440 * d))


@app.route('/datas/week', methods=['GET'])
def send_last_week():
    kill_producer()
    return jsonify(r.xrange('raspberry', '-', count=10080))


@app.route('/datas/week/<w>', methods=['GET'])
def send_weeks(w):
    kill_producer()
    if isinstance(w, int):
        return jsonify(r.xrange('raspberry', '-', count=10080 * w))


@app.route('/datas/month', methods=['GET'])
def send_last_month():
    kill_producer()
    return jsonify(r.xrange('raspberry', '-', count=43800))


@app.route('/datas/month/<m>', methods=['GET'])
def send_months(m):
    kill_producer()
    if isinstance(m, int):
        return jsonify(r.xrange('raspberry', '-', count=43800 * m))


# @app.route('/datas/year', methods=['GET'])
# def send_datas():
#     kill_producer()
#     return jsonify(r.xrange('raspberry', '-', count=525600))


# @app.route('/datas/year/<year>', methods=['GET'])
# def send_datas(year):
#     kill_producer()
#     if isinstance(year, int):
#         return jsonify(r.xrange('raspberry', '-', count=525600 * year))


@app.route('/datas/delete', methods=['GET'])
def delete_stream():
    kill_producer()
    if r.execute_command("DEL", "raspberry"):
        return jsonify('Fait')
    else:
        return jsonify('Pas fait')


@app.route('/datas/create', methods=['GET'])
def run_python_file():
    kill_producer()
    result = subprocess.run(["python", 'producer.py'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode())
    print(result.stderr.decode())
    return jsonify(result.stdout.decode())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
