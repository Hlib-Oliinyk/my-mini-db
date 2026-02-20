from .matcher import Matcher


class Query:
    def __init__(self, table):
        self._table = table
        self._filters: list[dict] = []
        self._limit: int | None = None
        self._order_by: str | None = None

    def filter(self, **kwargs):
        self._filters.append(kwargs)
        return self

    def all(self) -> list:
        result = []

        for row in self._table._rows.values():
            if Matcher._matches(row, self._filters):
                result.append(row.copy())

        if self._order_by is None:
            return result[:self._limit]

        sorted_result = sorted(result, key=lambda x: x[self._order_by])
        return sorted_result[:self._limit]

    def first(self) -> dict | None:
        for row in self._table._rows.values():
            if Matcher._matches(row, self._filters):
                return row.copy()

    def limit(self, limit_num: int):
        self._limit = limit_num
        return self

    def order_by(self, order_str: str):
        self._order_by = order_str
        return self