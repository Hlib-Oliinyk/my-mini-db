from .indexes.composite_index import CompositeIndex
from .indexes.factory import IndexFactory
from .indexes.index_base import IndexBase
from .query import Query
from .exceptions import IndexAlreadyExists


class Table:
    def __init__(self):
        self._rows: dict[int, dict] = {}
        self._next_id = 1
        self._indexes: dict[str | tuple, IndexBase] = {}

    def insert(self, data: dict) -> int:
        row_id = self._next_id
        self._rows[row_id] = data
        self._next_id += 1

        for field, index in self._indexes.items():

            if isinstance(index, CompositeIndex):
                if all(self._rows[row_id].get(key) for key in field):
                    value = tuple(self._rows[row_id].values())
                    index.add(row_id, value)
            else:
                if field in self._rows[row_id]:
                    value = self._rows[row_id][field]
                    index.add(row_id, value)

        return row_id

    def get(self, row_id: int) -> dict | None:
        if row_id not in self._rows:
            return None

        row = self._rows.get(row_id)
        return row.copy()

    def update(self, row_id: int, new_values: dict) -> int | None:
        row = self.get(row_id)

        for field, index in self._indexes.items():

            if isinstance(index, CompositeIndex):
                for field_part in field:

                    if field_part in row and field_part in new_values:
                        if row[field_part] != new_values[field_part]:

                            value = tuple(row[f] for f in field)
                            index.remove(row_id, value)

                            new_tuple = tuple(new_values.get(f, row[f]) for f in field)
                            index.add(row_id, new_tuple)

            else:
                if field in row and field in new_values:
                    if row[field] != new_values[field]:
                        index.remove(row_id, row[field])
                        index.add(row_id, new_values[field])

        row.update(new_values)
        self._rows[row_id] = row

        return row_id

    def delete(self, row_id: int) -> bool:
        if row_id not in self._rows:
            return False

        row = self.get(row_id)

        for field, index in self._indexes.items():

            if isinstance(index, CompositeIndex):
                value = tuple(row[f] for f in field)
                index.remove(row_id, value)
            else:
                value = row[field]
                index.remove(row_id, value)

        self._rows.pop(row_id)
        return True

    def query(self):
        return Query(self)

    def create_index(self, field: str | tuple, index_type: str):
        if field in self._indexes:
            raise IndexAlreadyExists()

        index = IndexFactory.create(index_type)

        for row_id, row_value in self._rows.items():

            if isinstance(field, tuple):
                value = tuple(row_value[f] for f in field)
                index.add(row_id, value)
            else:
                value = row_value[field]
                index.add(row_id, value)

        self._indexes[field] = index

    def remove_index(self, field: str) -> bool:
        if field not in self._indexes:
            return False

        self._indexes.pop(field)
        return True