"""
main module of OpenFlow Capture
"""
import argparse
import asyncio
import datetime
from logging import getLogger, DEBUG, StreamHandler, Formatter, handlers, INFO

from capture.capture import CaptureWithRepo, CaptureWithPipe, CaptureWithWeb, CaptureBase, SimpleCapture
from ofproto.packet import OFMsg
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


class OFCaptureBase:
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

        # capture
        self.capture: CaptureBase = SimpleCapture(observable=self.observable)

        if log_file:
            set_logger(log_level=log_level, filename=log_file)
        logger.info("OFCapture ready (lip={}, lport={}, cip={}, cport={}, async_queue={})".format(
            local_ip, local_port, controller_ip, controller_port, self.channel_manager.q_all
        ))

    def start_server(self, coro: list = None):
        self.event_loop.run_until_complete(self.start_server_coro(coro))

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

    def on(self, msg_type, handler=None):
        """

        Examples:

            # get only packet in message
            @ofcapture.on(10)
            def packetin_handler(msg):
                print(msg)

            # get all message
            @ofcapture.on("*")
            def all_msg_handler(msg):
                print(msg)
        """
        def set_handler(handler):
            self.capture.handlers[msg_type] = handler
            return handler
        if handler is None:
            return set_handler
        set_handler(handler)


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

    def start_server(self, coro: list = None):
        coro = coro if coro is not None else []
        self.event_loop.run_until_complete(self.start_server_coro([ws_server_start(self.ws_ip, self.ws_port), *coro]))

    def stop_server(self):
        super(OFCaptureWithWeb, self).stop_server()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--log_file', help="log file path", default=None)
    parser.add_argument('--ws_ip', help="web socket server ip address", default="0.0.0.0")
    parser.add_argument('--ws_port', help="web socket server port", default=8889)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    loglevel = DEBUG if args.verbose else INFO
    ofcapture = OFCaptureWithWeb(log_file=args.log_file, log_level=loglevel, ws_ip=args.ws_ip, ws_port=args.ws_port)

    try:
        ofcapture.start_server()
    except KeyboardInterrupt as e:
        logger.info("keyboardInterrupt : {}".format(str(e)))
        print(ofcapture.capture)
    exit()
