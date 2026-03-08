from .table import Table
from .exceptions import TableExists


class Database:
    def __init__(self):
        self._tables: dict[str, Table] = {}

    def create_table(self, table_name: str) -> Table:
        if table_name in self._tables.keys():
            raise TableExists(f"Table '{table_name}' already exists")

        table = self._tables[table_name] = Table()
        return table

    def get_table(self, table_name: str) -> Table | None:
        return self._tables.get(table_name)

    def drop_table(self, table_name: str) -> bool | None:
        if self.get_table(table_name):
            self._tables.pop(table_name)
            return True