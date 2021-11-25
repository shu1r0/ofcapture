from abc import ABCMeta, abstractmethod
from logging import getLogger
import asyncio

from ofproto.openflow import parse


class Observable(metaclass=ABCMeta):
    """Observable class"""

    @abstractmethod
    def register_observer(self, observer):
        """register observer.

        Args:
            observer (api.observer) :
        """

    @abstractmethod
    def remove_observer(self, observer):
        """remove observer

        Args:
            observer (api.observer) :
        """

    @abstractmethod
    def notify_observers(self, msg):
        """notify observers

        Args:
            msg (Message) :
        """


class ObservableData(Observable):
    """Observable Data class"""

    def __init__(self, data_queue):
        """init and start to search data

        Args:
            data_queue (asyncio.Queue) :
        """
        self.observers = set()
        self.data_queue = data_queue
        self.logger = getLogger("ofcapture." + __name__)

    async def start_search(self):
        """get msg from queue

        Notes:
            * This method block because this repeats the polling the queue
        """
        while True:
            msg = await self.data_queue.get()
            msgs = parse(msg, logger=self.logger)
            for m in msgs:
                self.notify_observers(m)

    def register_observer(self, observer):
        self.observers.add(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, msg):
        for observer in self.observers:
            self.logger.debug("notify data to observer: {}".format(msg))
            observer.update(msg)
