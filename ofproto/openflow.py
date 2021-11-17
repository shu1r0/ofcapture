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


def parse(msg, logger=None):
    """parse OpenFlow message

    Args:
        msg (Message) :
        logger (Logger) :

    Returns:
        (str, object, dict)
    """
    try:
        # header, _, _ = openflow.parser(msg.data)
        of_msg = unpack_message(msg.data)
        msg_name = of_msg.header.message_type.name
        dict_of_msg = todict(of_msg, logger)
        if logger:
            logger.info("Parsed msg : {} {} {}".format(msg_name, of_msg, dict_of_msg))
        return msg_name, of_msg, dict_of_msg
    except Exception as e:
        msg_name = get_header(msg)["header"].message_type.name
        if logger:
            logger.error("Failed to unpack msg({}) : {}".format(msg_name, str(e)))
        return msg_name, None, None


def get_header(msg):
    header = Header()
    header.unpack(msg.data[:header.get_size()])
    new_message = new_message_from_header(header)
    return {
        "header": new_message.header,
        "message_size": new_message.get_size()
    }


def todict(obj, logger=None, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, logger, classkey)
        return data
    if isinstance(obj, bytes):  # bytes convert test
        value = ""
        for v in obj:
            v = hex(v)[2:]
            value += v
        return value
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
