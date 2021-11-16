
class Datapath:

    def __init__(self):
        self.local_port = -1
        self.datapath_id: int = -1
        self.ports: list[Port] = []


class Port:

    def __init__(self):
        self.port_no: int or None = None
        self.pad = None
        self.hw_addr: str or None = None
        self.pad2 = None
        self.name: str or None = None
        self.config: str or None = None
        self.state: str or None = None
        self.curr: str or None = None
        self.advertised: str or None = None
        self.supported: str or None = None
        self.peer: str or None = None
        self.curr_speed: int or None = None
        self.max_speed: int or None

    @classmethod
    def from_dict(cls, dct):
        port = cls()
        for key in dct.keys():
            setattr(port, key, dct[key])
