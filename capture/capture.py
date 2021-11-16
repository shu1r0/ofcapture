import pickle

from pyof.foundation.basic_types import DPID
from pyof.v0x04.common.header import Type
from pyof.v0x04.controller2switch.common import MultipartType

from proxy.observer import OFObserver
from capture.of_msg_repository import packet_in_out_repo
from ofproto.packet import OFMsg
from ofproto.datapath import Port, Datapath as Dp
from ofproto.openflow import todict

from web.proto.api_pb2 import Datapath, OpenFlowMessage, OpenFlowMessages
from web.ws_server import emit_ofmsg, set_getOpenFlowMessage_handler


class CaptureBase(OFObserver):
    """CaptureBase

    This is a base class for saving messages to a repository or output to stdout.
    """

    def __init__(self, observable):
        super(CaptureBase, self).__init__(observable)
        self.lport_to_dpid = {}
        self.lport_to_port = {}
        self._messages = []
        self._datapathes: list[Datapath] = []

    def msg_handler(self, msg):
        """handle msg

        Args:
            msg (OFMsg) : openflow message object
        """
        datapath = self._get_datapath(msg.local_port)
        if datapath is None:
            datapath = Dp()
            # self.logger.info("local_port type = {}".format(type(msg.local_port)))
            datapath.local_port = msg.local_port
            self._datapathes.append(datapath)

        if msg.message_type == Type.OFPT_FEATURES_REPLY:
            # set datapath id
            if isinstance(msg.of_msg.datapath_id, DPID):
                datapath_id = int(''.join(msg.of_msg.datapath_id.value.split(':')))
                self.lport_to_dpid[msg.local_port] = datapath_id
                datapath.datapath_id = datapath_id
        elif msg.message_type == Type.OFPT_MULTIPART_REPLY:
            if msg.of_msg.multipart_type == MultipartType.OFPMP_PORT_DESC:
                # Note: OFPMP_PORT_DESC message body is a list of port
                port_list = []
                for p in msg.of_msg.body:
                    port_list.append(Port.from_dict(todict(p)))
                self.lport_to_port[msg.local_port] = port_list
                datapath.ports = port_list

        if msg.local_port in self.lport_to_dpid.keys():
            msg.datapath_id = self.lport_to_dpid[msg.local_port]
        self._messages.append(msg)

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
            send_types = [Type.OFPT_PACKET_OUT, Type.OFPT_PACKET_IN, Type.OFPT_FLOW_MOD]
            if msg.message_type in send_types:
                # pre-pickle to avoid error
                msg.of_msg = msg.of_msg.pack()
                msg = pickle.dumps(msg)
                self.parent_conn.send_bytes(msg)

    def get_packet_in_out_repo(self):
        return packet_in_out_repo


class CaptureWithWeb(CaptureBase):

    def __init__(self, observable):
        super(CaptureWithWeb, self).__init__(observable)
        self.messages = []

        set_getOpenFlowMessage_handler(self._get_ofmsgs)

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
        proto_OFMsg.switch2controller = msg.switch2controller
        self.messages.append(proto_OFMsg)
        emit_ofmsg(proto_OFMsg.SerializeToString())

    def _get_ofmsgs(self, _request):
        ofmsgs = OpenFlowMessages()
        for m in self.messages:
            ofmsgs.messages.append(m)
        self.messages = []
        return ofmsgs.SerializeToString()

