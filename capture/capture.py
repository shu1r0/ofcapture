from pyof.v0x04.common.header import Type
from pyof.foundation.basic_types import DPID

from proxy.observer import OFObserver
from capture.of_msg_repository import packet_in_out_repo


class CaptureBase(OFObserver):
    """CaptureBase

    This is a base class for saving messages to a repository or output to stdout.
    """

    def __init__(self, observable):
        super(CaptureBase, self).__init__(observable)

    def get_msg(self, msg):
        pass


class CaptureWithRepo(CaptureBase):
    """

    Todo:
        * to get ofport from phy_port
    """

    def __init__(self, observable):
        super(CaptureWithRepo, self).__init__(observable)
        self.port_to_dpid = {}
        self.ports = {}

    def get_msg(self, msg):
        if msg.message_type == Type.OFPT_FEATURES_REPLY:
            if isinstance(msg.of_msg.datapath_id, DPID):
                self.port_to_dpid[msg.local_port] = int(''.join(msg.of_msg.datapath_id.value.split(':')))
        if msg.message_type == Type.OFPT_MULTIPART_REPLY:
            # save port to name
            self.ports.setdefault(msg.local_port, {})
            for port in msg.of_msg.body:
                self.ports[msg.local_port][int(port.port_no)] = str(port.name)
        self.add_repo(msg)

    def add_repo(self, msg):
        if msg.message_type == Type.OFPT_PACKET_OUT:
            self.logger.debug("add repo {}".format(msg))
            packet_in_out_repo.add(msg)
        elif msg.message_type == Type.OFPT_PACKET_IN:
            self.logger.debug("add repo {}".format(msg))
            packet_in_out_repo.add(msg)

    def get_packet_in_out_repo(self):
        return packet_in_out_repo

    def get_datapathid(self, port):
        return self.port_to_dpid[port]

    def get_port(self, datapath_id):
        if not isinstance(datapath_id, int):
            datapath_id = int(datapath_id)
        for p, d in self.port_to_dpid.items():
            if d == datapath_id:
                return p

    def get_port_name(self, port, port_no):
        return self.ports[port][port_no]


class CaptureWithPipe(CaptureBase):
    """

    Todo:
        * to get ofport from phy_port
    """

    def __init__(self, observable, parent_conn=None):
        super(CaptureWithPipe, self).__init__(observable)
        self.parent_conn = parent_conn
        self.port_to_dpid = {}
        self.ports = {}

    def get_msg(self, msg):
        if msg.message_type == Type.OFPT_FEATURES_REPLY:
            if isinstance(msg.of_msg.datapath_id, DPID):
                self.port_to_dpid[msg.local_port] = int(''.join(msg.of_msg.datapath_id.value.split(':')))
        if msg.message_type == Type.OFPT_MULTIPART_REPLY:
            # save port to name
            self.ports.setdefault(msg.local_port, {})
            for port in msg.of_msg.body:
                self.ports[msg.local_port][int(port.port_no)] = str(port.name)
        self.send_pipe(msg)

    def send_pipe(self, msg):
        if self.parent_conn:
            if msg.message_type == Type.OFPT_PACKET_OUT:
                self.parent_conn.send(msg)
            elif msg.message_type == Type.OFPT_PACKET_IN:
                self.parent_conn.send(msg)

    def get_packet_in_out_repo(self):
        return packet_in_out_repo

    def get_datapathid(self, port):
        return self.port_to_dpid[port]

    def get_port(self, datapath_id):
        if not isinstance(datapath_id, int):
            datapath_id = int(datapath_id)
        for p, d in self.port_to_dpid.items():
            if d == datapath_id:
                return p

    def get_port_name(self, port, port_no):
        return self.ports[port][port_no]
