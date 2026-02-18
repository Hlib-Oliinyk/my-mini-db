
class Matcher:

    @staticmethod
    def _matches(row: dict, filters: dict) -> bool:
        for key, value in filters.items():
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

        return True