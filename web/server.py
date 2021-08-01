from flask import Flask, render_template
from flask_socketio import SocketIO

async_mode = None

app = Flask(__name__, static_folder="./html/dist/static", template_folder="./html/dist")
app.config['SECRET_KEY'] = "keysecret!"

socketio = SocketIO(app, async_mode=async_mode)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/ws')
def connect_handler():
    socketio.emit('connected', {'msg': "connected"})


if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
