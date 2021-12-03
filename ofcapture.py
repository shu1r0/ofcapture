"""
main module of OpenFlow Capture

Todo:
    * Encapsulate OpenFlo Capture
"""
import asyncio
import datetime
from abc import ABCMeta
from logging import getLogger, DEBUG, StreamHandler, Formatter, handlers, INFO

from capture.capture import CaptureWithRepo, CaptureWithPipe, CaptureWithWeb
from proxy.proxy import ChannelManager, SwitchHandler
from proxy.observable import ObservableData

from web.ws_server import ws_server_start, ws_server_stop


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
    """OpenFlow proxy to capture

    Attributes:
        channel_manager (ChannelManager) :
        observable (Observable) : observable instance
        switch_handler (SwitchHandler) : local server
        event_loop (asyncio.EventLoop) : event loop
    """

    def __init__(self, local_ip='127.0.0.1', local_port=63333, controller_ip='127.0.0.1', controller_port=6633,
                 event_loop=None, log_file=None, log_level=INFO):
        self.event_loop = event_loop if event_loop else asyncio.get_event_loop()
        # TCP client
        self.channel_manager = ChannelManager(loop=self.event_loop,
                                              controller_ip=controller_ip,
                                              controller_port=controller_port)
        # observable OpenFlow message
        self.observable = ObservableData(self.channel_manager.q_all)
        # local server
        self.switch_handler = SwitchHandler(host=local_ip,
                                            port=local_port,
                                            loop=self.event_loop,
                                            channel_manager=self.channel_manager)

        if log_file:
            set_logger(log_level=log_level, filename=log_file)
        logger.info("OFCapture ready (lip={}, lport={}, cip={}, cport={}, async_queue={})".format(
            local_ip, local_port, controller_ip, controller_port, self.channel_manager.q_all
        ))

    def start_server(self):
        self.event_loop.run_until_complete(self.start_server_coro())

    async def start_server_coro(self, coro: list = None):
        coro = coro if coro is not None else []
        await asyncio.gather(*[
            self.switch_handler.start_server(),
            self.observable.start_search(),
            *coro
        ], loop=self.event_loop)

    def stop_server(self):
        self.event_loop.stop()
        self.event_loop.close()


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
        super(OFCaptureWithPipe, self).__init__(local_ip=local_ip, local_port=local_port,
                                                controller_ip=controller_ip, controller_port=controller_port,
                                                event_loop=event_loop, log_file=log_file, log_level=log_level)
        self.capture = CaptureWithPipe(self.observable, parent_conn=parent_conn)


class OFCaptureWithWeb(OFCaptureBase):

    def __init__(self, log_file=None, log_level=INFO, ws_ip="0.0.0.0", ws_port=8889):
        super(OFCaptureWithWeb, self).__init__(log_file=log_file, log_level=log_level)
        self.capture = CaptureWithWeb(self.observable)
        self.ws_ip = ws_ip
        self.ws_port = ws_port

    def start_server(self):
        self.event_loop.run_until_complete(self.start_server_coro([ws_server_start(self.ws_ip, self.ws_port)]))

    def stop_server(self):
        super(OFCaptureWithWeb, self).stop_server()


if __name__ == "__main__":
    ofcapture = OFCaptureWithWeb(log_file=default_logfile, log_level=INFO, ws_ip="10.0.0.109")
    try:
        ofcapture.start_server()
    except KeyboardInterrupt as e:
        logger.info("keyboardInterrupt : {}".format(str(e)))
        print(ofcapture.capture)
        # ofcapture.stop_server()
    exit()
