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

        if self._order_by is None:
            return result[:self._limit]

        sorted_result = sorted(result, key=lambda x: x[self._order_by])

        return sorted_result[:self._limit]

    def all(self) -> list:
        return self._execute()

    def first(self) -> dict | None:
        result = self._execute()
        return result[0] if result else None