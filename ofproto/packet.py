import macaddress
import ipaddress
from enum import Enum
from datetime import datetime

from pyof.foundation.base import GenericMessage, UBIntBase, GenericBitMask, GenericType




class OFMsg:
    """Message"""

    def __init__(self, timestamp, local_ip, remote_ip, local_port, remote_port, data, switch2controller):
        """

        Args:
            timestamp (float) : timestamp
            local_ip (str) : local ip address (=switch)
            remote_ip (str) : remote ip address (=controller)
            local_port (int) : local port number (=switch)
            remote_port (int) : remote port number (=controller)
            data (bytes) : message data
            switch2controller (bool) : Was the data sent from switch to controller?
        """
        self.timestamp = timestamp
        self.local_ip = local_ip
        self.remote_ip = remote_ip
        self.local_port = local_port
        self.remote_port = remote_port
        self.datapath_id = None
        self.data = data
        self.switch2controller = switch2controller
        self.of_msg = None

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.timestamp)

    @property
    def message_type(self):
        """OpenFlow message type"""
        if self.of_msg:
            return self.of_msg.header.message_type
        else:
            return None

    @property
    def msg_name(self):
        return self.message_type.name

    @property
    def xid(self):
        if self.of_msg:
            return self.of_msg.header.xid
        else:
            return None

    @classmethod
    def parse_to_dict(cls, msg):
        d = todict(msg.of_msg)
        d["timestamp"] = msg.timestamp
        d["datapath_id"] = msg.datapath_id
        d["switch_to_controller"] = msg.switch2controller
        return d

    def __repr__(self):
        return "<Message msg_name={} of_msg={} timestamp={} local_port={} datapath_id={}>"\
            .format(self.msg_name, self.of_msg, self.timestamp, self.local_port, self.datapath_id)


def macaddress_bytes2string(data):
    addr = macaddress.MAC(data)
    return str(addr).replace('-', ':').lower()


def ipv4address_bytes2string(data):
    addr = ipaddress.IPv4Address(data)
    return str(addr)

def todict(obj, logger=None, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, logger, classkey)
        return data
    elif isinstance(obj, bytes):  # bytes convert test
        # value = ""
        # for v in obj:
        #     v = hex(v)[2:]
        #     value += v
        return obj
    elif isinstance(obj, Enum):
        name = obj.name
        return name
    elif hasattr(obj, "_ast"):
        return todict(obj._ast(), logger)
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, logger, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        # value
        if isinstance(obj, GenericType):
            # logger.debug("UBIntBase, key : {}".format(vars(obj)))
            if obj.enum_ref is None:
                return obj._value
            elif isinstance(obj._value, GenericBitMask):
                return obj._value.__str__()
        elif isinstance(obj, Enum):
            return obj.value
        data = dict([(key, todict(value, logger, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


