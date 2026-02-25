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

    def remove(self, row_id: int, row_value: dict) -> bool:
        if self.field in row_value:
            value = self.storage.get(row_value[self.field])

            if value is None:
                return False

            if row_id not in value:
                return False

            self.storage[row_value[self.field]].discard(row_id)

            if not self.storage[row_value[self.field]]:
                del self.storage[row_value[self.field]]

            return True

    def update(self, row_id: int, old_row_value: dict, new_row_value: dict):
        if self.field in new_row_value and self.field in old_row_value:
            if old_row_value[self.field] != new_row_value[self.field]:
                self.remove(row_id, old_row_value)
                self.add(row_id, new_row_value)