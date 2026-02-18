
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