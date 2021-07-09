from api.observer import OFObserver

class CaputerFlowTables(OFObserver):

    def __init__(self, observable):
        super().__init__(observable)
        self.pipeline = None

    def dict_ofmsg_handler(self, dict_of_msg, msg):
        self.logger.info("get msg {}".format(msg.msg_name))
