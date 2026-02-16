
class Table:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._rows: dict[int, dict] = {}
        self._next_id = 1

    @staticmethod
    def _matches(row: dict, filters: dict) -> bool:
        return all(row.get(k) == v for k,v in filters.items())

    def insert(self, data: dict) -> int:
        row_id = self._next_id
        self._rows[row_id] = data
        self._next_id += 1
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
            if self._matches(row, filters):
                mathing_ids.append(row_id)

        for row_id in mathing_ids:
            self.update_by_id(row_id, values)

        return len(mathing_ids)

    def delete_by_id(self, row_id: int) -> bool:
        if row_id not in self._rows:
            return False

        self._rows.pop(row_id)
        return True