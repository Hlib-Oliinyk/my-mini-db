
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

    def update_by_id(self, row_id: int, values: dict) -> int | None:
        updated_row = self.get(row_id)
        updated_row.update(values)

        self._rows[row_id] = updated_row
        return row_id

    def update(self, filters: dict, values: dict):
        for row_id, row in self._rows.items():
            if all(row.get(k) == v for k,v in filters.items()):
                self.update_by_id(row_id, values)

            return row