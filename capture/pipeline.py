from ryu.ofproto.ofproto_v1_3_parser import OFPMatch, OFPInstruction, OFPFlowMod

class FlowEntry():
    """

    * see A.3.4.1 Modify Flow Entry Message in `<https://opennetworking.org/wp-content/uploads/2014/10/openflow-spec-v1.3.0.pdf>`_

    """

    def __init__(self, match, priority, counters, instructions, timeouts, cookie=None):
        """

        Args:
            match (OFPMatch) :
            priority:
            counters:
            instructions (list of OFPInstruction) :
            timeouts:
            cookie:
        """
        self.match = match  # n
        self.priority = priority  # n
        self.counters = counters
        self.instructions = instructions  # n
        # Note: idle_timeout is treated as hard_timeout
        self.timeouts = timeouts  # n
        self.cookies = cookie

class FlowTable():

    def __init__(self):
        self.flow_entries = []

    def insert_flow(self, flow):
        pass

    def delete_flow(self, flow):
        pass

    def dump_flows(self):
        return self.flow_entries.copy()

class PipelineBase():

    def __init__(self):
        self.flow_tables = {}
        self.group_tables = None
        self.meter_table = None

    def modify(self, flow_mod):
        """

        Args:
            flow_mod (OFPFlowMod) :

        Returns:

        """

        flow_entry = None
