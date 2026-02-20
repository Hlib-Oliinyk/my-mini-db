from .matcher import Matcher
from .exceptions import KeyNotExist


class Query:
    def __init__(self, table):
        self._table = table
        self._filters: list[dict] = []
        self._limit: int | None = None
        self._order_by: str | None = None

    def filter(self, **kwargs):
        self._filters.append(kwargs)
        return self

    def limit(self, limit_num: int):
        self._limit = limit_num
        return self

    def order_by(self, order_str: str):
        self._order_by = order_str
        return self

    def _finder(self) -> list:
        result = []

        for row in self._table._rows.values():
            if Matcher._matches(row, self._filters):
                result.append(row.copy())

        return result

    def _execute(self) -> list:
        result = self._finder()

        if self._order_by:
            if result and self._order_by not in result[0]:
                raise KeyNotExist(f"Key '{self._order_by}' not exists")

            result = sorted(result, key=lambda x: x[self._order_by])
        if self._limit is not None:
            return result[:self._limit]

        return result

    def all(self) -> list:
        return self._execute()

    def first(self) -> dict | None:
        result = self._execute()
        return result[0] if result else None