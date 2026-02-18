from .table import Table


class Database:
    def __init__(self):
        self._tables: dict[str, Table] = {}

    def create_table(self, table_name: str) -> Table:
        table = self._tables[table_name] = Table()
        return table

    def get_table(self, table_name: str) -> Table | None:
        return self._tables.get(table_name)

    def drop_table(self, table_name: str) -> bool:
        if self.get_table(table_name):
            self._tables.pop(table_name)
            return True