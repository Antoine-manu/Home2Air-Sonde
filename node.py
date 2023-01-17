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
    print(f"No running process found for producer.py")
    return False


@app.route('/datas/kill', methods=['GET'])
def kill():
    if kill_producer():
        return jsonify('Fait')
    else:
        return jsonify('Pas fait')


@app.route('/datas', methods=['GET'])
def send_datas():
    kill_producer()
    return jsonify(r.xrange('raspberry', '-', '+'))


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
