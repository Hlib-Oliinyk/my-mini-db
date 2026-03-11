from abc import ABC, abstractmethod
from typing import Any


class IndexBase(ABC):

    @abstractmethod
    def add(self, row_id: int, value: Any):
        pass

    @abstractmethod
    def remove(self, row_id: int, value: Any):
        pass

    @abstractmethod
    def find(self, operator: str, value: Any) -> set[int] | None:
        pass