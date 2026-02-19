from .matcher import Matcher


class Query:
    def __init__(self, table):
        self._table = table
        self._filters: list[dict] = []
        self._limit = None

    def filter(self, **kwargs):
        self._filters.append(kwargs)
        return self

    def all(self) -> list:
        result = []

        for row in self._table._rows.values():
            if Matcher._matches(row, self._filters):
                result.append(row.copy())

        return result

    def first(self) -> dict:
        for row in self._table._rows.values():
            if Matcher._matches(row, self._filters):
                return row