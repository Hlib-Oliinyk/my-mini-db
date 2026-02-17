
class Query:
    def __init__(self, table):
        self._table = table
        self._filters = []

    def filter(self, **kwargs):
        self._filters.append(kwargs)
        return self

    def all(self):
        matches = []

        for row in self._table._rows.values():
            if all(
                all(row.get(k) == v for k,v in f.items())
                for f in self._filters
            ):
                matches.append(row.copy())

        return matches