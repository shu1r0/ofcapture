from abc import ABCMeta, abstractmethod
from logging import getLogger

from proxy.observable import Observable


class OFObserver(metaclass=ABCMeta):

    def __init__(self, observable):
        """init params and register for observable

        Args:
            observable (Observable) :
        """
        self.observable = observable
        self.observable.register_observer(self)
        self.logger = getLogger("ofcapture." + __name__)

    @abstractmethod
    def update(self, msg):
        pass

