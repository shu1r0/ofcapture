from datetime import datetime


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
        self.data = data
        self.switch2controller = switch2controller
        self.msg_name = None
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

    def __repr__(self):
        return "<Message msg_name={} of_msg={} timestamp={}>".format(self.msg_name, self.of_msg, self.timestamp)
