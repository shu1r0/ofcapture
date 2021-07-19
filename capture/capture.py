from pyof.v0x04.common.header import Type

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
            # save datapath id
            self.port_to_dpid[msg.local_port] = int(msg.of_msg.datapath_id)
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
