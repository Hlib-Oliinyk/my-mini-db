
class Matcher:

    @staticmethod
    def _matches(row: dict, filters: list) -> bool:
        for f in filters:
            for key, value in f.items():
                if "__" in key:
                    field, operator = key.split("__")
                else:
                    field = key
                    operator = "eq"

                data_field = row.get(field)

                if operator == "eq":
                    if data_field != value:
                        return False

                if operator == "gt":
                    if data_field is None or data_field < value:
                        return False

                if operator == "lt":
                    if data_field is None or data_field > value:
                        return False

                if operator == "contains":
                    if data_field is None or value not in data_field:
                        return False

        return True

    @staticmethod
    def _matches_with_id(rows: dict[int, dict], filters: list) -> list:
        result = []

        row_id = None

        for f in filters:
            for key, value in f.items():
                if key == "id":
                    row_id = value

        if row_id is not None and row_id in rows.keys():
            row = rows.get(row_id)
            result.append(row.copy())

        for value in rows.values():
            if Matcher._matches(value, filters):
                result.append(value.copy())

        return result




