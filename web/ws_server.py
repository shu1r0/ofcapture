from aiohttp import web
import asyncio
import socketio
from logging import getLogger, setLoggerClass, Logger

from web.proto.api_pb2 import OpenFlowMessageRequest

setLoggerClass(Logger)
logger = getLogger('ofcapture.web.ws_server')


# Web Socket Server Name space
NAME_SPACE = ''


# socket server
# CORSのオリジン設定をすべて許可に
socketio_server = socketio.AsyncServer(cors_allowed_origins='*')

# web application
web_app = web.Application()
socketio_server.attach(web_app)
runner = web.AppRunner(web_app)


#
# ↓ Web Socket event
#

@socketio_server.event(namespace=NAME_SPACE)
def connect(sid, environ, auth):
    logger.info('connect sid={}'.format(sid))


@socketio_server.event(namespace=NAME_SPACE)
def disconnect(sid):
    logger.info('disconnect sid={}'.format(sid))


@socketio_server.event(namespace=NAME_SPACE)
def connected(sid, data):
    pass


handler_getOpenFlowMessage = None
def set_getOpenFlowMessage_handler(handler):
    global handler_getOpenFlowMessage
    handler_getOpenFlowMessage = handler


@socketio_server.event(namespace=NAME_SPACE)
def getOpenFlowMessage(sid, data):
    request = OpenFlowMessageRequest()
    result = handler_getOpenFlowMessage(request)
    emit_get_ofmsg(result)


def emit_ofmsg(data):
    asyncio.ensure_future(socketio_server.emit("flowOpenFlowMessage", data))



def emit_get_ofmsg(data):
    asyncio.ensure_future(socketio_server.emit("getOpenFlowMessage", data))



#
# ↓ Web server start and stop
#

async def ws_server_start(ip="0.0.0.0", port=8888):
    await runner.setup()
    site = web.TCPSite(runner, host=ip, port=port)
    await site.start()
    # await asyncio.Event().wait()


async def ws_server_stop():
    await runner.cleanup()


if __name__ == '__main__':

    def callback(event, param):
        print(str(event) + str(param))

    ws_server_start()
