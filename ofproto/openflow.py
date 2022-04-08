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
            logger.info("Parsed msg : {} {} ".format(msg.msg_name, of_msg))

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
