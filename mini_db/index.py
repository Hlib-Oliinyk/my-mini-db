from typing import Any


class Index:
    def __init__(self, field: str):
        self.field = field
        self.storage: dict[Any, set[int]] = {}

    def add(self, row_id: int, row_value: dict):
        if self.field in row_value:
            if row_value[self.field] in self.storage:
                self.storage[row_value[self.field]].add(row_id)
            else:
                self.storage[row_value[self.field]] = {row_id}