from .matcher import Matcher
from .exceptions import KeyNotExist, RowNotExists, MultipleObjectReturn


class Query:
    def __init__(self, table):
        self._table = table
        self._filters: list[dict] = []
        self._limit: int | None = None
        self._order_by: str | None = None
        self._offset: int | None = None

    @staticmethod
    def _clone_row(row_id: int, row_value: dict) -> dict:
        new_row = {}

        new_row["id"] = row_id
        for key, value in row_value.items():
            new_row[key] = value

        return new_row

    def filter(self, **kwargs):
        self._filters.append(kwargs)
        return self

    def limit(self, limit_num: int):
        self._limit = limit_num
        return self

    def order_by(self, order_str: str):
        self._order_by = order_str
        return self

    def offset(self, offset_num: int):
        self._offset = offset_num
        return self

    def _finder(self) -> list:
        result = []

        for row_id, row_value in self._table._rows.items():
            row = Query._clone_row(row_id, row_value)
            if Matcher._matches(row, self._filters):
                result.append(row)

        return result

    def _execute(self) -> list:
        result = self._finder()

        if self._order_by:
            if result and self._order_by not in result[0]:
                raise KeyNotExist(f"Key '{self._order_by}' not exists")

            result = sorted(result, key=lambda x: x[self._order_by])

        if self._offset is not None:
            result = result[self._offset:]

        if self._limit is not None:
            result = result[:self._limit]

        return result

    def all(self) -> list:
        return self._execute()

    def first(self) -> dict | None:
        result = self._execute()
        return result[0] if result else None

    def count(self) -> int:
        return len(self._finder())

    def exists(self) -> bool:
        if self._finder():
            return True
        return False

    def get(self, **kwargs) -> dict | None:
        self.filter(**kwargs)

        result = self._finder()

        if len(result) == 0:
            raise RowNotExists()
        if len(result) > 1:
            raise MultipleObjectReturn()

        return result[0]



