from abc import ABC, abstractmethod


class StrategyBase(ABC):
    def __init__(self, config, exchangeshandler) -> None:
        self._config = config
        self.exchangeshandler = exchangeshandler

    @abstractmethod
    def check_opportunity(self):
        pass
