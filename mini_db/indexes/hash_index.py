from typing import Any

from .index_base import IndexBase


class HashIndex(IndexBase):
    def __init__(self):
        super().__init__()
        self.storage: dict[Any, set[int]] = {}

    def add(self, row_id: int, value: Any):
        if value in self.storage:
            self.storage[value].add(row_id)
        else:
            self.storage[value] = {row_id}

    def remove(self, row_id: int, value: Any) -> bool:
        if value not in self.storage:
            return False

        if value is None:
            return False

        if row_id not in self.storage[value]:
            return False

        self.storage[value].discard(row_id)

        if not self.storage[value]:
            del self.storage[value]

        return True

    def find(self, operator: str, value: Any) -> set[int] | None:
        if operator != "eq":
            return None

        if value in self.storage:
            return self.storage.get(value).copy()
        else:
            return set()