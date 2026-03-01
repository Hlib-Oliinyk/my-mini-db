import bisect

from typing import Any

from .index_base import IndexBase


class RangeIndex(IndexBase):
    def __init__(self):
        super().__init__()
        self.storage: dict[Any, set[int]] = {}
        self.sorted_keys = []

    def add(self, row_id: int, value: Any):
        if value in self.storage:
            self.storage[value].add(row_id)
        else:
            self.storage[value] = {row_id}
            bisect.insort(self.sorted_keys, value)


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
            self.sorted_keys.remove(value)

        return True

    def find(self, operator: str, value: Any) -> set[int] | None:
        if operator == "eq":
            if value in self.storage:
                return self.storage.get(value).copy()
            else:
                return set()

        if operator == "gt":
            num_index = bisect.bisect_right(self.sorted_keys, value)
            candidate_values = self.sorted_keys[num_index:]

            result = set()

            for candidate in candidate_values:
                result.update(self.storage[candidate])
            return result

        if operator == "lt":
            num_index = bisect.bisect_left(self.sorted_keys, value)
            candidate_values = self.sorted_keys[:num_index]

            result = set()

            for candidate in candidate_values:
                result.update(self.storage[candidate])
            return result

        return set()