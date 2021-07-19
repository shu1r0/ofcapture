from abc import ABCMeta, abstractmethod


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

    def pop(self, port, until=None, count=None):
        if until is not None:
            return self._pop_until(port, until)
        elif count is not None:
            return self._pop_count(port, count)
        else:
            return self._pop(port)

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


packet_in_out_repo = PacketInOutRepository()
