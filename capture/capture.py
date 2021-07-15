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

    def __init__(self, observable):
        super(CaptureWithRepo, self).__init__(observable)
        self.port_to_dpid = {}

    def get_msg(self, msg):
        if msg.message_type == Type.OFPT_FEATURES_REPLY:
            # save datapath id
            self.port_to_dpid[msg.local_port] = msg.of_msg.datapath_id
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
