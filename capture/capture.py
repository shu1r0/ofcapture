import pickle

from pyof.foundation.basic_types import DPID
from pyof.v0x04.common.header import Type
from pyof.v0x04.controller2switch.common import MultipartType

from proxy.observer import OFObserver
from capture.of_msg_repository import packet_in_out_repo
from util.packet import OFMsg

from web.proto.api_pb2 import Datapath, OpenFlowMessage


class CaptureBase(OFObserver):
    """CaptureBase

    This is a base class for saving messages to a repository or output to stdout.
    """

    def __init__(self, observable):
        super(CaptureBase, self).__init__(observable)
        self.lport_to_dpid = {}
        self.lport_to_port = {}

    def msg_handler(self, msg):
        """handle msg

        Args:
            msg (OFMsg) : openflow message object
        """
        if msg.message_type == Type.OFPT_FEATURES_REPLY:
            # set datapath id
            if isinstance(msg.of_msg.datapath_id, DPID):
                self.lport_to_dpid[msg.local_port] = int(''.join(msg.of_msg.datapath_id.value.split(':')))
        if msg.message_type == Type.OFPT_MULTIPART_REPLY:
            if msg.of_msg.multipart_type == MultipartType.OFPMP_PORT_DESC:
                # Note: OFPMP_PORT_DESC message body is a list of port
                self.lport_to_port[msg.local_port] = msg.of_msg.body

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
        for port in self.lport_to_port[local_port]:
            if int(port_no) == port_no:
                return port.name
        return None


class CaptureWithRepo(CaptureBase):
    """

    Todo:
        * to get ofport from phy_port
    """

    def __init__(self, observable):
        super(CaptureWithRepo, self).__init__(observable)
        self.repo = packet_in_out_repo

    def msg_handler(self, msg):
        super(CaptureWithRepo, self).msg_handler(msg)
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

    def msg_handler(self, msg):
        super(CaptureWithPipe, self).msg_handler(msg)
        self.send_pipe(msg)

    def send_pipe(self, msg):
        if self.parent_conn:
            if msg.message_type == Type.OFPT_PACKET_OUT:
                if msg.local_port in self.lport_to_dpid.keys():
                    msg.datapath_id = self.lport_to_dpid[msg.local_port]
                # pre-pickle to avoid error
                msg.of_msg = msg.of_msg.pack()
                msg = pickle.dumps(msg)
                self.parent_conn.send_bytes(msg)
            elif msg.message_type == Type.OFPT_PACKET_IN:
                if msg.local_port in self.lport_to_dpid.keys():
                    msg.datapath_id = self.lport_to_dpid[msg.local_port]
                # pre-pickle to avoid error
                msg.of_msg = msg.of_msg.pack()
                msg = pickle.dumps(msg)
                self.parent_conn.send_bytes(msg)

    def get_packet_in_out_repo(self):
        return packet_in_out_repo


class CaptureWithWeb(CaptureBase):

    def __init__(self, observable, socketio):
        super(CaptureWithWeb, self).__init__(observable)
        self.socketio = socketio

    def msg_handler(self, msg):
        super(CaptureWithWeb, self).msg_handler(msg)
        proto_datapath = Datapath()
        proto_datapath.local_port = str(msg.local_port)
        dpid = self.get_datapathid(msg.local_port)
        if dpid:
            proto_datapath.id = str(dpid)
        else:
            proto_datapath.id = ""
        proto_OFMsg = OpenFlowMessage()
        proto_OFMsg.datapath.local_port = proto_datapath.local_port
        proto_OFMsg.datapath.id = proto_datapath.id
        proto_OFMsg.xid = int(msg.of_msg.header.xid)
        proto_OFMsg.message_type = msg.msg_name
        proto_OFMsg.timestamp = msg.timestamp
        self.socketio.emit('getOpenFlowMessage', proto_OFMsg.SerializeToString())

