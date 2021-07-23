from abc import ABCMeta, abstractmethod
from logging import getLogger, setLoggerClass, Logger


setLoggerClass(Logger)
logger = getLogger('ofcapture.of_msg_repository')


class AbstractOFMessageRepository(metaclass=ABCMeta):

    def __init__(self):
        self.repository = {}

    @abstractmethod
    def add(self, msg):
        raise NotImplementedError

    @abstractmethod
    def pop(self, port, until=None, count=None):
        raise NotImplementedError


class OFMessageRepository(AbstractOFMessageRepository):

    def __init__(self):
        super(OFMessageRepository, self).__init__()

    def add(self, msg):
        self.repository.setdefault(msg.local_port, [])
        self.repository[msg.local_port].append(msg)
        logger.debug("added msg {} to repo {}".format(msg, self.repository))

    def pop(self, port, until=None, count=None):
        try:
            if until is not None:
                return self._pop_until(port, until)
            elif count is not None:
                return self._pop_count(port, count)
            else:
                return self._pop(port)
        except KeyError:
            logger.error("Failed to pop from of repository (repo={})".format(self.repository))
            return None

    def _pop(self, port):
        return self.repository.pop(port)

    def _pop_until(self, port, until):
        tmp_i = []
        msgs = self.repository[port]
        for i in range(len(msgs)):
            if msgs[i].timestamp < until:
                tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, msgs.pop(i))
        return tmp

    def _pop_count(self, port, count):
        tmp_i = []
        msgs = self.repository[port]
        for i in range(min(len(msgs), count)):
            tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, msgs.pop(i))
        return tmp


class PacketInOutRepository(OFMessageRepository):
    """repository for packet_in and packet_out"""

    def __init__(self):
        super(PacketInOutRepository, self).__init__()

    def add(self, msg):
        if msg.datapath_id:
            self.repository.setdefault(msg.datapath_id, [])
            self.repository[msg.datapath_id].append(msg)
            logger.debug("added msg {} to repo {}".format(msg, self.repository))

    def pop(self, datapath_id, until=None, count=None):
        try:
            if until is not None:
                return self._pop_until(datapath_id, until)
            elif count is not None:
                return self._pop_count(datapath_id, count)
            else:
                return self._pop(datapath_id)
        except KeyError:
            logger.error("Failed to pop from of repository (repo={})".format(self.repository))
            return None

    def _pop(self, datapath_id):
        return self.repository.pop(datapath_id)

    def _pop_until(self, datapath_id, until):
        tmp_i = []
        msgs = self.repository[datapath_id]
        for i in range(len(msgs)):
            if msgs[i].timestamp < until:
                tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, msgs.pop(i))
        return tmp

    def _pop_count(self, datapath_id, count):
        tmp_i = []
        msgs = self.repository[datapath_id]
        for i in range(min(len(msgs), count)):
            tmp_i.append(i)
        tmp = []
        for i in tmp_i[::-1]:
            tmp.insert(0, msgs.pop(i))
        return tmp


packet_in_out_repo = PacketInOutRepository()
