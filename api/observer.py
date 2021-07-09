from abc import ABCMeta, abstractmethod
from logging import getLogger
import json
import util.openflow


from proxy.observable import Observable
from capture.of_msg_repository import packet_in_out_repo


class AbstractObserver(metaclass=ABCMeta):

    @abstractmethod
    def update(self, msg):
        """update method

        Args:
            msg (Message) : OpenFlow msg
        """


class OFObserver(AbstractObserver):

    def __init__(self, observable):
        """init params and register for observable

        Args:
            observable (Observable) :
        """
        self.observable = observable
        self.observable.register_observer(self)
        self.logger = getLogger(__name__)

    def update(self, msg):
        self.logger.debug("observed from observable: {}".format(msg.data[:8]))  # 8 : header Byte size
        msg_name, of_msg, dict_of_msg = util.openflow.parse(msg, self.logger)
        msg.set_msg_name(msg_name)
        self.add_repo(msg)
        # self.dict_ofmsg_handler(dict_of_msg, msg)

    def dict_ofmsg_handler(self, dict_of_msg, msg):
        """

        Args:
            dict_ofmsg (dict) :
            msg (Message) :
        """
        pass

    def add_repo(self, msg):
        if msg.msg_name == "OFPT_PACKETOUT":
            self.logger.debug("add repo {}".format(msg))
            packet_in_out_repo.add(msg)

