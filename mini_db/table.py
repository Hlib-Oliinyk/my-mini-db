from .query import Query
from .matcher import Matcher
from .index import Index


class Table:
    def __init__(self):
        self._rows: dict[int, dict] = {}
        self._next_id = 1
        self._indexes: dict[str, Index] = {}

    def insert(self, data: dict) -> int:
        row_id = self._next_id
        self._rows[row_id] = data
        self._next_id += 1

        for index in self._indexes.values():
            index.add(row_id, data)

        return row_id

    def get(self, row_id: int) -> dict | None:
        if row_id not in self._rows:
            return None

        row = self._rows.get(row_id)
        return row.copy()

    def update_by_id(self, row_id: int, values: dict) -> int | None:
        updated_row = self.get(row_id)
        updated_row.update(values)

        self._rows[row_id] = updated_row
        return row_id

    def update(self, filters: dict, values: dict) -> int:
        mathing_ids = []

        for row_id, row in self._rows.items():
            if Matcher._matches(row, [filters]):
                mathing_ids.append(row_id)

        for row_id in mathing_ids:
            self.update_by_id(row_id, values)

        return len(mathing_ids)

    def delete_by_id(self, row_id: int) -> bool:
        if row_id not in self._rows:
            return False

        self._rows.pop(row_id)
        return True

    def select(self, **kwargs) -> list[dict]:
        result = []

        for row in self._rows.values():
            if Matcher._matches(row, [kwargs]):
                result.append(row.copy())

        return result

    def query(self):
        return Query(self)

    def create_index(self, field: str):
        index = Index(field)
        for row_id, row_value in self._rows.items():
            index.add(row_id, row_value)

        self._indexes[field] = index

    def remove_index(self, filed: str) -> bool:
        if filed not in self._indexes:
            return False

        self._indexes.pop(filed)
        return True
