from abc import ABCMeta, abstractmethod
from logging import getLogger
import json
from util.openflow import parse, get_header


from proxy.observable import Observable
from capture.of_msg_repository import packet_in_out_repo
from util.packet import OFMsg


class AbstractObserver(metaclass=ABCMeta):

    @abstractmethod
    def update(self, msg):
        """update method

        Args:
            msg (Message) : OpenFlow msg
        """


class OFObserver(AbstractObserver, metaclass=ABCMeta):

    def __init__(self, observable):
        """init params and register for observable

        Args:
            observable (Observable) :
        """
        self.observable = observable
        self.observable.register_observer(self)
        self.logger = getLogger("ofcapture." + __name__)

    def update(self, msg):
        self.logger.debug("observed from observable: {}".format(msg.data[:8]))  # 8 : header Byte size
        msg_name, of_msg, dict_of_msg = parse(msg, self.logger)
        if of_msg:
            msg.msg_name = msg_name
            msg.of_msg = of_msg
            self.msg_handler(msg)
        else:
            result = get_header(msg)
            header = result["header"]
            msg_size = result["message_size"]
            data1 = msg.data[:int(header.length)]
            data2 = msg.data[int(header.length):]
            msg1 = msg
            msg1.data = data1
            msg2 = OFMsg(msg.timestamp, msg.local_ip, msg.remote_ip, msg.local_port, msg.remote_port, data2, msg.switch2controller)
            self.logger.debug("message separate (data1={}, data2={})".format(data1, data2))
            for m in [msg1, msg2]:
                msg_name, of_msg, dict_of_msg = parse(m, self.logger)
                m.msg_name = msg_name
                m.of_msg = of_msg
                self.msg_handler(m)

    @abstractmethod
    def msg_handler(self, msg):
        pass

