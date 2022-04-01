"""
Capture App
"""

import pickle
from abc import ABCMeta, abstractmethod

from pyof.foundation.basic_types import DPID
from pyof.v0x04.common.header import Type
from pyof.v0x04.controller2switch.common import MultipartType

from proxy.observer import OFObserver
from capture.of_msg_repository import packet_in_out_repo
from ofproto.packet import OFMsg
from ofproto.datapath import Port, Datapath
from ofproto.openflow import todict

import web.proto.api_pb2 as pb
from web.ws_server import emit_ofmsg, set_getOpenFlowMessage_handler


class CaptureBase(OFObserver, metaclass=ABCMeta):
    """CaptureBase

    This is a base class for saving messages to a repository or output to stdout.
    """

    def __init__(self, observable, do_capture=True):
        super(CaptureBase, self).__init__(observable)
        # local port to datapath id mapping
        self.lport_to_dpid = {}
        # local port to port obj mapping
        self.lport_to_port = {}

        # all captured messages
        self._messages = []
        self.do_capture = do_capture
        # datapathes
        self._datapathes: list[Datapath] = []

    def update(self, msg):
        """handle msg

        * this method called by observable

        Args:
            msg (OFMsg) : openflow message object
        """
        # datapthes
        datapath = self._get_datapath(msg.local_port)
        if datapath is None:
            datapath = Datapath()
            datapath.local_port = msg.local_port
            self._datapathes.append(datapath)

        # set datapathid
        if msg.message_type == Type.OFPT_FEATURES_REPLY:
            # set datapath id
            if isinstance(msg.of_msg.datapath_id, DPID):
                datapath_id = int(''.join(msg.of_msg.datapath_id.value.split(':')), 16)
                self.lport_to_dpid[msg.local_port] = datapath_id
                datapath.datapath_id = datapath_id
        # set port obj
        elif msg.message_type == Type.OFPT_MULTIPART_REPLY:
            if msg.of_msg.multipart_type == MultipartType.OFPMP_PORT_DESC:
                # Note: OFPMP_PORT_DESC message body is a list of port
                port_list = []
                for p in msg.of_msg.body:
                    port_list.append(Port.from_dict(todict(p)))
                self.lport_to_port[msg.local_port] = port_list
                datapath.ports = port_list

        # update msg datapath id (before FeaturesReply)
        if msg.local_port in self.lport_to_dpid.keys():
            msg.datapath_id = self.lport_to_dpid[msg.local_port]

        if self.do_capture:
            self._messages.append(msg)

        # notify subclass
        self.msg_handler(msg)

    @abstractmethod
    def msg_handler(self, msg):
        raise NotImplementedError

    def get_datapathid(self, local_port):
        """get datapath id

        Args:
            local_port (int) : local port

        Returns:
            int or None : datapath id
        """
        if local_port in self.lport_to_dpid.keys():
            return self.lport_to_dpid[local_port]
        else:
            return None

    def _get_datapath(self, local_port: int):
        datapath = None
        for d in self._datapathes:
            if d.local_port == local_port:
                datapath = d
                break
        return datapath

    def get_port(self, datapath_id):
        """get local port of datapath

        Args:
            datapath_id (int or string) : Datapath ID that can be converted to int.

        Returns:
            int or None : local port
        """
        if not isinstance(datapath_id, int):
            datapath_id = int(datapath_id)
        for p, d in self.lport_to_dpid.items():
            if d == datapath_id:
                return p
        return None

    def get_port_name(self, local_port, port_no):
        """get port name from port number
        """
        for port in self.lport_to_port[local_port]:
            if int(port_no) == port_no:
                return port.name
        return None

    def __str__(self):
        msgs = ""
        for msg in self._messages:
            datapathid = self.get_datapathid(msg.local_port)
            order = "switch(dpid={}) -> controller".format(datapathid)
            if not msg.switch2controller:
                order = "controller -> switch(dpid={})".format(datapathid)
            msg_name = "{}(xid={})".format(msg.msg_name, msg.xid)

            msgs += "{} {} {} \n".format(msg.datetime, order, msg_name)
        return msgs


class SimpleCapture(CaptureBase):

    def __init__(self, observable):
        super(SimpleCapture, self).__init__(observable)

    def msg_handler(self, msg):
        pass


class CaptureWithRepo(CaptureBase):
    """

    Todo:
        * to get ofport from phy_port
    """

    def __init__(self, observable):
        super(CaptureWithRepo, self).__init__(observable)
        self.repo = packet_in_out_repo

    def msg_handler(self, msg):
        self.add_repo(msg)

    def add_repo(self, msg):
        if msg.message_type == Type.OFPT_PACKET_OUT:
            self.logger.debug("add repo {}".format(msg))
            self.repo.add(msg)
        elif msg.message_type == Type.OFPT_PACKET_IN:
            self.logger.debug("add repo {}".format(msg))
            self.repo.add(msg)

    def get_packet_in_out_repo(self):
        return self.repo


class CaptureWithPipe(CaptureBase):
    """

    Todo:
        * to get ofport from phy_port
    """

    def __init__(self, observable, parent_conn=None):
        super(CaptureWithPipe, self).__init__(observable)
        self.parent_conn = parent_conn
        self._send_types = [Type.OFPT_PACKET_OUT, Type.OFPT_PACKET_IN, Type.OFPT_FLOW_MOD]

    def msg_handler(self, msg):
        self.send_pipe(msg)

    def send_pipe(self, msg):
        if self.parent_conn:
            if msg.message_type in self._send_types:
                # pre-pickle to avoid error
                msg.of_msg = msg.of_msg.pack()
                msg = pickle.dumps(msg)
                self.parent_conn.send_bytes(msg)

    def get_packet_in_out_repo(self):
        return packet_in_out_repo


class CaptureWithWeb(CaptureBase):
    """
    Capture With Web
    """

    def __init__(self, observable):
        super(CaptureWithWeb, self).__init__(observable, do_capture=True)
        # protobuf messages
        self.messages = []

        set_getOpenFlowMessage_handler(self._get_ofmsgs)

    def msg_handler(self, msg):
        proto_datapath = pb.Datapath()
        proto_datapath.local_port = str(msg.local_port)
        dpid = self.get_datapathid(msg.local_port)
        if dpid:
            proto_datapath.id = str(dpid)
        else:
            proto_datapath.id = ""
        proto_OFMsg = pb.OpenFlowMessage()
        proto_OFMsg.datapath.local_port = proto_datapath.local_port
        proto_OFMsg.datapath.id = proto_datapath.id
        proto_OFMsg.xid = int(msg.of_msg.header.xid)
        proto_OFMsg.message_type = msg.msg_name
        proto_OFMsg.timestamp = msg.timestamp
        proto_OFMsg.switch2controller = msg.switch2controller
        proto_OFMsg.content = str(todict(msg.of_msg))
        self.messages.append(proto_OFMsg)
        emit_ofmsg(proto_OFMsg.SerializeToString())

    def _get_ofmsgs(self, _request):
        ofmsgs = pb.OpenFlowMessages()
        for m in self.messages:
            ofmsgs.messages.append(m)
        self.messages = []
        return ofmsgs.SerializeToString()

