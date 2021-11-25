"""
OpenFlow parser module

This module provides methods to decode OpenFlow messages.
This hides various external OpenFlow modules to ofcaputure.
"""

from enum import Enum

from pyof.foundation.base import GenericMessage, UBIntBase, GenericBitMask, GenericType
# from pyof.utils import unpack
from pyof.v0x04.common.header import Header
from pyof.v0x04.common.utils import unpack_message, new_message_from_header, MESSAGE_TYPES
from ryu.lib.packet.openflow import openflow
from ryu.lib.packet.stream_parser import StreamParser
from ryu.ofproto.ofproto_v1_3_parser import msg_parser, OFPPacketOut

from ofproto.packet import OFMsg


def parse(msg, logger=None):
    """parse OpenFlow message

    Args:
        msg (Message) :
        logger (Logger) :

    Returns:
        list[Message]
    """
    msgs = []
    try:
        header = get_header(msg)
        data = msg.data[:int(header.length)]
        rest = msg.data[int(header.length):]
        msg.data = data

        of_msg = unpack_message(msg.data)
        msg.of_msg = of_msg

        msgs.append(msg)

        if logger:
            dict_of_msg = todict(of_msg, logger)
            logger.info("Parsed msg : {} {} {}".format(msg.msg_name, of_msg, dict_of_msg))

        if len(rest) > 0:
            msg_rest = OFMsg(msg.timestamp, msg.local_ip, msg.remote_ip, msg.local_port, msg.remote_port,
                             rest, msg.switch2controller)
            rest_msgs = parse(msg_rest, logger=logger)
            msgs.extend(rest_msgs)

        return msgs
    except Exception as e:
        msg_name = get_header(msg).message_type.name
        if logger:
            logger.error("Failed to unpack msg({}) : {}".format(msg_name, str(e)))
    return []


def get_header(msg):
    header = Header()
    header.unpack(msg.data[:header.get_size()])
    return header


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
