"""
main module of OpenFlow Capture

Todo:
    * Encapsulate OpenFlo Capture
"""
import asyncio
import datetime
import threading
from abc import ABCMeta, abstractmethod
from logging import getLogger, DEBUG, StreamHandler, Formatter, handlers, INFO

from capture.capture import CaptureWithRepo, CaptureWithPipe, CaptureWithWeb
from proxy.proxy import ChannelManager, SwitchHandler
from proxy.observable import ObservableData

from web.server import app, socketio


logger = getLogger("ofcapture")
default_logfile = "log/" + "ofcapture-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用


def set_logger(log_level=DEBUG, filename=default_logfile):
    logger.setLevel(log_level)
    formatter = Formatter(
        "%(asctime)s | %(process)d | %(name)s, %(funcName)s, %(lineno)d | %(levelname)s | %(message)s")
    # handler = StreamHandler()
    # handler.setLevel(DEBUG)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    handler = handlers.RotatingFileHandler(filename=filename,
                                           maxBytes=16777216,
                                           backupCount=2)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class OFCaptureBase(metaclass=ABCMeta):

    def __init__(self, log_file=None, log_level=INFO):
        # set logger
        if log_file:
            set_logger(log_level=log_level, filename=log_file)

    @abstractmethod
    def start_server(self):
        raise NotImplementedError


class OFCapture(OFCaptureBase):
    """OpenFlow proxy to capture

    Attributes:
        channel_manager (ChannelManager) :
        observable (Observable) : observable instance
        capture (Observer) : observer instance
        switch_handler (SwitchHandler) : local server
        event_loop (asyncio.EventLoop) : event loop
    """

    def __init__(self, local_ip='127.0.0.1', local_port=63333, controller_ip='127.0.0.1', controller_port=6633,
                 event_loop=None, log_file=None, log_level=INFO):
        super(OFCapture, self).__init__(log_file=log_file, log_level=log_level)
        self.event_loop = event_loop
        if self.event_loop is None:
            self.event_loop = asyncio.get_event_loop()
        # TCP client
        self.channel_manager = ChannelManager(loop=self.event_loop,
                                              controller_ip=controller_ip,
                                              controller_port=controller_port)
        # observable OpenFlow message
        self.observable = ObservableData(self.channel_manager.get_queue_all_data())
        # OpenFlow message observer
        self.capture = CaptureWithRepo(self.observable)
        # local server
        self.switch_handler = SwitchHandler(host=local_ip,
                                            port=local_port,
                                            loop=self.event_loop,
                                            channel_manager=self.channel_manager)

    def start_server(self):
        self.event_loop.run_until_complete(asyncio.wait([
            self.start_server_coro()
        ]))

    async def start_server_coro(self):
        await self.switch_handler.start_server()

    def server_restart(self):
        raise NotImplementedError


class OFCaptureWithPipe(OFCaptureBase):
    """OpenFlow proxy to capture with pipe

    Attributes:
        channel_manager (ChannelManager) :
        observable (Observable) : observable instance
        capture (Observer) : observer instance
        switch_handler (SwitchHandler) : local server
        event_loop (asyncio.EventLoop) : event loop
    """

    def __init__(self, local_ip='127.0.0.1', local_port=63333, controller_ip='127.0.0.1', controller_port=6633,
                 event_loop=None, log_file=None, log_level=INFO, parent_conn=None):
        super(OFCaptureWithPipe, self).__init__(log_file=log_file, log_level=log_level)
        self.event_loop = event_loop
        if self.event_loop is None:
            self.event_loop = asyncio.get_event_loop()
        self.channel_manager = ChannelManager(loop=self.event_loop,
                                              controller_ip=controller_ip,
                                              controller_port=controller_port)
        self.observable = ObservableData(self.channel_manager.get_queue_all_data())
        self.capture = CaptureWithPipe(self.observable, parent_conn=parent_conn)
        self.switch_handler = SwitchHandler(host=local_ip,
                                            port=local_port,
                                            loop=self.event_loop,
                                            channel_manager=self.channel_manager)

        if log_file:
            set_logger(log_level=log_level, filename=log_file)

    def start_server(self):
        self.event_loop.run_until_complete(asyncio.wait([
            self.start_server_coro()
        ]))

    async def start_server_coro(self):
        await self.switch_handler.start_server()

    def server_restart(self):
        raise NotImplementedError


class OFCaptureWithWeb(OFCapture):

    def __init__(self, log_file=None, log_level=INFO):
        super(OFCaptureWithWeb, self).__init__(log_file=log_file, log_level=log_level)
        # thread = threading.Thread(target=socketio.run, kwargs={"app": app, "debug": True, "port": 8080})
        # socketio.run(app, debug=True, port=8080)
        # thread.start()
        self.capture = CaptureWithWeb(self.observable, socketio)

    def start_server(self):
        t = threading.Thread(target=super(OFCaptureWithWeb, self).start_server)
        t.start()
        # asyncio.ensure_future(self.start_server_coro())
        socketio.run(app, debug=True, port=8080)


if __name__ == "__main__":
    from proxy.proxy import Channel

    @Channel.filter
    def filter(data, switch2controller):
        logger.debug("filter (data={}, s2c={})".format(data, switch2controller))
        return data

    ofcapture = OFCapture(log_file=default_logfile, log_level=DEBUG)
    try:
        ofcapture.start_server()
    except KeyboardInterrupt as e:
        logger.info("keyboardInterrupt : {}".format(str(e)))

    exit()
