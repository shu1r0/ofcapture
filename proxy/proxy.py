"""Proxy Module

Todo:
    * to create reconnecting method
    * to create openflow packet obj
"""
import asyncio
from datetime import datetime
from logging import getLogger, Logger

from util.packet import OFMsg


class Channel:
    """OpenFlow channel"""

    def __init__(self, queue):
        """init

        Args:
            queue (asyncio.Queue) : queue to store packet
        """
        self.q_all = queue
        self.logger = getLogger("ofcapture." + __name__)
        self.switch_handler = None
        self.switch_writer = None
        self.controller_handler = None
        self.controller_writer = None

    def set_switch_handler(self, switch_handler):
        """set switch handler to send switch

        Args:
            switch_handler (SwitchHandler) :
        """
        self.switch_handler = switch_handler

    def set_controller_handler(self, controller_handler):
        """set controller handler to send controller

        Args:
            controller_handler (ControllerHandler) :
        """
        self.controller_handler = controller_handler

    def set_switch_writer(self, switch_writer):
        """set StreamWriter to send switch

        Args:
            switch_writer (asyncio.StreamWriter) :
        """
        self.switch_writer = switch_writer

    def set_controller_writer(self, controller_writer):
        """set StreamWriter to send controller

        Args:
            controller_writer (asyncio.StreamWriter) :
        """
        self.controller_writer = controller_writer

    async def send_to_controller(self, data):
        """set data and sent to controller

        Args:
            data (bytes) : data that is sent to controller

        Returns:
            int : -1 if failed to send
        """
        if not self.is_closing():
            await self.controller_handler.send_to_controller(self.controller_writer, data)
            await self._put_queue_all(data, switch2controller=True)
            self.logger.debug("set data and sent to controller : {}".format(data))
            return 0
        else:
            self.logger.warning("Failed to send to controller : {}".format(data))
            return -1

    async def send_to_switch(self, data):
        """set data and sent to switch

        Args:
            data (bytes) : data that is sent to switch

        Returns:
            int : -1 if failed to send
        """
        if not self.is_closing():
            await self.switch_handler.send_to_switch(self.switch_writer, data)
            await self._put_queue_all(data, switch2controller=False)
            self.logger.debug("set data and sent to switch : {}".format(data))
            return 0
        else:
            self.logger.warning("Failed to send to switch : {}".format(data))
            return -1

    async def _put_queue_all(self, data, switch2controller):
        """put data as message

        Args:
            data (bytes) : data
            switch2controller (bool) : Was the data sent from switch to controller?
        """
        timestamp = datetime.now().timestamp()
        local_ip, local_port = self.switch_writer.get_extra_info('peername')
        remote_ip, remote_port = self.controller_writer.get_extra_info('peername')
        msg = OFMsg(timestamp, local_ip, remote_ip, local_port, remote_port, data, switch2controller)
        await self.q_all.put(msg)

    def is_closing(self):
        """Is this channel closing?

        Returns:
            bool : Is this channel established?
        """
        is_closing = True
        if self.switch_writer is not None and self.controller_writer is not None\
                and self.switch_handler is not None and self.controller_handler is not None:
            is_closing = self.switch_writer.is_closing() or self.controller_writer.is_closing()

        if is_closing:
            self.logger.debug("is_closing is {}, s writer is {}, c writer is {}, s handler is {}, c handler is {},"
                              " s writer close? {}, c writer close? {}"
                              .format(is_closing, self.switch_writer is not None, self.controller_writer is not None,
                                      self.switch_handler is not None, self.controller_handler is not None,
                                      self.switch_writer.is_closing(), self.controller_writer.is_closing()))
        return is_closing



class ChannelManager:
    """Channel Manager
    * This has queue that holds all data and gives the queue to api_module
    * This creates new channel

    Attributes:
        q_all (asyncio.Queue) : all data (from switch and controller)
        logger (Logger) : logger
        has_switch_join (bool) : True if a switch has join
        has_controller_join (bool) : True if a controller has join
        controller_handler (ControllerHandler) : client communicating with controller
    """

    def __init__(self, loop, controller_ip='127.0.0.1', controller_port=6633):
        """

        Args:
            loop (asyncio.AbstractEventLoop) : event loop
            controller_ip (str) : controller ip
            controller_port (int) : controller port
        """
        self.q_all = asyncio.Queue()
        self.logger = getLogger("ofcapture." + __name__)

        self.has_switch_join = False
        self.has_controller_join = False

        self.controller_handler = ControllerHandler(controller_ip, controller_port, loop, self)

    async def create_channel(self, switch_handler, switch_writer):
        """create openflow channel

        Args:
            switch_handler (SwitchHandler) : switch connection handler
            switch_writer (StreamWriter) : switch writer

        Returns:
            Channel or None : OpenFlow channel. If the controller cannot be connected, return None.
        """
        try:
            channel = Channel(self.q_all)
            controller_writer = await self.controller_handler.open_connection(channel)
            if controller_writer:
                channel.set_switch_handler(switch_handler)
                channel.set_switch_writer(switch_writer)
                channel.set_controller_handler(self.controller_handler)
                channel.set_controller_writer(controller_writer)
                return channel
            else:
                self.logger.debug("no connectable controller")
                return None
        except Exception as e:
            raise

    def get_queue_all_data(self):
        """queue for all traffic data

        Returns:
            asyncio.Queue
        """
        return self.q_all

    def _has_open_channel(self):
        has_open_channel = self.has_switch_join and self.has_controller_join
        return has_open_channel


class SwitchHandler:
    """server communicating with switches

    Attributes:
        host (str) : switch ip
        port (int) : switch port
        loop (asyncio.AbstractEventLoop) : event loop
        channel_manager (ChannelManager) : channel manager
        logger (Logger) : logger
        switches (set) : switch set
    """

    def __init__(self, host, port, loop, channel_manager):
        """init SwitchHandler

        Args:
            host (str) : switch ip
            port (int) : switch port
            loop (asyncio.AbstractEventLoop) :
            channel_manager (ChannelManager) :
        """
        self.host = host
        self.port = port
        self.loop = loop
        self.channel_manager = channel_manager
        self.logger = getLogger("ofcapture." + __name__)

        self.switches = set()

    async def start_server(self):
        """start server"""
        server = await asyncio.start_server(self.handle_switch, host=self.host, port=self.port)
        self.logger.info("Server on {}".format(server.sockets[0].getsockname()))

        async with server:
            self.logger.info("Server serve forever {}".format(server.sockets[0].getsockname()))
            await server.serve_forever()

    async def handle_switch(self, reader, writer):
        """Accepting connections from switches

        This creates a channel and receives data from the switch.
        This tries to send the received data to the controller, if the connection is established.
        If the connection is not established, the data is discarded.

        Args:
            reader (asyncio.StreamReader) :
            writer (asyncio.StreamWriter) :

        Returns:

        """
        peername = writer.get_extra_info('peername')
        self.logger.info("Client {} is connected".format(peername))
        self.switches.add(peername)
        self.channel_manager.has_switch_join = True

        channel = await self.channel_manager.create_channel(self, writer)
        if channel is None:
            writer.close()
            return

        try:
            while True:
                self.logger.debug("waiting data ......")
                # 64000 is default buffer size
                data = await reader.read(64000)
                self.logger.debug("read {}".format(data))
                if not data:
                    self.logger.debug("no data from switch read")
                    break
                if not channel.is_closing():
                    await channel.send_to_controller(data)
                else:
                    self.logger.debug("the channel is closing")
                    break
        except BrokenPipeError as e:
            self.logger.error("Failed to read: {}".format(str(e)))
        except ConnectionResetError as e:
            self.logger.error("Failed to read: {}".format(str(e)))
        except Exception as e:
            self.logger.error("Failed to read: {}".format(str(e)))
            raise
        finally:
            self.logger.info("Close the connection and do exit processing")
            self.switches.remove(peername)
            if len(self.switches) == 0:
                self.channel_manager.has_switch_join = False
            writer.close()

    async def send_to_switch(self, writer, data):
        """send data to switch if queue has data

        Args:
            writer (asyncio.StreamWriter) :
            data (bytes) : data from controller

        Returns:

        """
        try:
            if not writer.is_closing():
                writer.write(data)
                await writer.drain()
                self.logger.debug("sent data to switch: {}".format(data))
            else:
                self.logger.debug("channel is closed")
        except ConnectionResetError as e:
            self.logger.info("Connection reset: {}".format(str(e)))


class ControllerHandler:
    """client communicating with controller

    Attributes:
        host (str) :
        port (int) :
        loop (asyncio.AbstractEventLoop) :
        channel_manager (ChannelManager) :
    """

    def __init__(self, host, port, loop, channel_manager):
        """init SwitchHandler

        Args:
            host (str) :
            port (int) :
            loop (asyncio.AbstractEventLoop) :
            channel_manager (ChannelManager) :
        """
        self.host = host
        self.port = port
        self.loop = loop
        self.channel_manager = channel_manager
        self.logger = getLogger("ofcapture." + __name__)

        self.controllers = set()

    async def open_connection(self, channel):
        """try to connect to controller

        Args:
            channel (Channel) :

        Returns:
            asyncio.StreamWriter or None : if succeeded to connect, return writer, else None
        """
        try:
            reader, writer = await asyncio.open_connection(host=self.host, port=self.port, loop=self.loop)
            asyncio.ensure_future(self.handle_controller(reader, writer, channel))
        except ConnectionRefusedError as e:
            self.logger.error("Failed to connect to controller : {}".format(str(e)))
            return None
        else:
            return writer

    async def handle_controller(self, reader, writer, channel):
        """

        Args:
            reader (asyncio.StreamReader) :
            writer (asyncio.StreamWriter) :
            channel (Channel) :
        """
        peername = writer.get_extra_info('peername')
        self.logger.info("connected Controller {}".format(peername))
        self.controllers.add(peername)
        self.channel_manager.has_controller_join = True
        try:
            while True:
                self.logger.debug("waiting data ......")
                data = await reader.read(64000)
                self.logger.debug("read {}".format(data))
                if not data:
                    self.logger.debug("no data from controller read")
                    break
                if not channel.is_closing():
                    await channel.send_to_switch(data)
                else:
                    self.logger.debug("the channel is close")
                    if channel.controller_writer is not None:
                        break
        except Exception as e:
            self.logger.error("Failed to read: {}".format(str(e)))
            raise
        finally:
            self.logger.info("Close the connection and do exit processing")
            self.controllers.remove(peername)
            if len(self.controllers) == 0:
                self.channel_manager.has_controller_join = False
            writer.close()

    async def send_to_controller(self, writer, data):
        """send data to controller if queue has data

        Args:
            writer (asyncio.StreamWriter) :
            data (bytes) :
        """
        try:
            if not writer.is_closing():
                writer.write(data)
                await writer.drain()
                self.logger.debug("sent data to controller: {}".format(data))
            else:
                self.logger.debug("channel is closed")
        except ConnectionResetError as e:
            self.logger.info("Connection reset: {}".format(str(e)))
        except Exception as e:
            self.logger.error("Connection error: {}".format(str(e)))
            raise
