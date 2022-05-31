from abc import ABC, abstractmethod


class AbstractSnapshot(ABC):
    @abstractmethod
    def get_time(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_state(self):
        pass
