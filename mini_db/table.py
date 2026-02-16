
class Table:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._rows: dict[int, dict] = {}
        self._next_id = 1

    def insert(self, data: dict) -> int:
        row_id = self._next_id
        self._rows[row_id] = data
        self._next_id += 1
        return row_id

    def get(self, row_id: int) -> dict | None:
        row = self._rows.get(row_id)
        return row.copy()