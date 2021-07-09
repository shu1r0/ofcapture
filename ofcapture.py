"""
main module of OpenFlow Capture

Todo:
    * Encapsulate OpenFlo Capture
"""
import asyncio
import datetime
from logging import getLogger, DEBUG, StreamHandler, Formatter, handlers

from capture.capture import CaptureWithRepo
from proxy.proxy import ChannelManager, SwitchHandler
from proxy.observable import ObservableData

logger = getLogger()


def setup_logger():
    logger.setLevel(DEBUG)
    formatter = Formatter(
        "%(asctime)s | %(process)d | %(name)s, %(funcName)s, %(lineno)d | %(levelname)s | %(message)s")
    handler = StreamHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    filename = "ofcapture-" + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".log"  # debug用
    handler = handlers.RotatingFileHandler(filename="log/" + filename,
                                           maxBytes=16777216,
                                           backupCount=2)
    handler.setLevel(DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class OFCapture:
    """OpenFlow proxy to capture

    Attributes:
        channel_manager (ChannelManager) :
        observable (Observable) : observable instance
        observer (Observer) : observer instance
        switch_handler (SwitchHandler) : local server
        event_loop (asyncio.EventLoop) : event loop
    """

    def __init__(self, local_ip='127.0.0.1', local_port=63333, controller_ip='127.0.0.1', controller_port=6633,
                 event_loop=None, logger=None):
        self.event_loop = event_loop
        if self.event_loop is None:
            self.event_loop = asyncio.get_event_loop()
        self.channel_manager = ChannelManager(loop=self.event_loop,
                                              controller_ip=controller_ip,
                                              controller_port=controller_port)
        self.observable = ObservableData(self.channel_manager.get_queue_all_data())
        self.observer = CaptureWithRepo(self.observable)
        self.switch_handler = SwitchHandler(host=local_ip,
                                            port=local_port,
                                            loop=self.event_loop,
                                            channel_manager=self.channel_manager)

    def start_server(self):
        self.event_loop.run_until_complete(asyncio.wait([
            self.switch_handler.start_server()
        ]))

    def server_restart(self):
        raise NotImplementedError

#
# def main():
#     setup_logger()
#
#     # datamanager
#     channel_manager = ChannelManager(loop)
#
#     # observer
#     observable = ObservableData(channel_manager.get_queue_all_data())
#     observer = CaputerFlowTables(observable)
#
#     # handler
#     switch_handler = SwitchHandler('127.0.0.1', 63333, loop, channel_manager)
#
#     loop.run_until_complete(asyncio.wait([
#         switch_handler.start_server()
#     ]))
#


if __name__ == "__main__":
    setup_logger()
    ofcapture = OFCapture(logger=logger)
    try:
        ofcapture.start_server()
    except KeyboardInterrupt as e:
        logger.info("keyboardInterrupt : {}".format(str(e)))

    exit()
