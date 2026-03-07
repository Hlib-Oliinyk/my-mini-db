
class Matcher:

    @staticmethod
    def _matches(row_data: dict, filters: list) -> bool:
        for f in filters:
            for key, value in f.items():
                if "__" in key:
                    field, operator = key.split("__")
                else:
                    field = key
                    operator = "eq"

                row_field = row_data.get(field)

                if operator == "eq":
                    if row_field != value:
                        return False

                if operator == "gt":
                    if row_field is None or row_field <= value:
                        return False

                if operator == "lt":
                    if row_field is None or row_field >= value:
                        return False

                if operator == "contains":
                    if row_field is None or value not in row_field:
                        return False

        return True

    @staticmethod
    def _match_operators(_filter: dict):
        for key, value in _filter.items():
            if "__" in key:
                field, operator = key.split("__")
            else:
                field = key
                operator = "eq"

            return operator, field, value

    @staticmethod
    def _filter_map(filters: list) -> dict:
        result = {}

        for _filter in filters:
            key = list(_filter.keys())[0]
            value = list(_filter.values())[0]

            result[key] = value

        return result
