from mini_db.matcher import Matcher
from mini_db.indexes.composite_index import CompositeIndex
from mini_db.exceptions import KeyNotExist
from mini_db.utils import timer


class QueryExecutor:
    def __init__(self, query_state):
        self.query_state = query_state

    @staticmethod
    def _merge_two_rows(row_one: dict, row_two: dict) -> dict:
        merged = row_one.copy()

        for key, value in row_two.items():
            merged[key] = value

        return merged

    def get_candidate_ids(self, filters: list) -> set[int]:
        candidate_ids = set()
        indexes_find_value = {}
        used_index = False
        filter_map = Matcher.filter_map(filters)

        for index_field, index in self.query_state.table_indexes.items():

            if isinstance(index, CompositeIndex):
                if all(key in filter_map for key in index_field):

                    value = tuple(filter_map.get(field) for field in index_field)
                    find = index.find("eq", value)
                    return find

        for _filter in filters:
            operator, field, value = Matcher.match_operators(_filter)

            if field in self.query_state.table_indexes:
                index = self.query_state.table_indexes[field]
                find = index.find(operator, value)

                indexes_find_value["__".join([field, operator])] = find

                if find is None:
                    continue

                if len(find) == 0:
                    return set()

        if len(indexes_find_value) != 0:
            used_index = True
            min_index_value = min(indexes_find_value.values(), key=len)

            for index_value in indexes_find_value.values():
                if len(candidate_ids) == 0:
                    candidate_ids = min_index_value
                else:
                    candidate_ids = candidate_ids.intersection(index_value)

        if used_index:
            return candidate_ids
        else:
            return set(self.query_state.table_rows.keys())

    def finder(self) -> list:
        result = []
        candidate_ids = self.get_candidate_ids(self.query_state.filters)

        for row_id in candidate_ids:
            row = self.query_state.table_rows[row_id].copy()

            if Matcher.matches(row, self.query_state.filters):
                row["row_id"] = row_id
                result.append(row)

        return result

    def _count_targets(self) -> int:
        target_count = None

        if self.query_state.limit is not None:
            if self.query_state.offset is not None:
                target_count = self.query_state.limit + self.query_state.offset
            else:
                target_count = self.query_state.limit

        return target_count

    def _index_scan(self) -> list:
        result = []
        target_count = self._count_targets()

        index = self.query_state.table_indexes[self.query_state.order_by[0]]
        sorted_keys = index.sorted_keys

        if self.query_state.order_by[1] == "desc":
            sorted_keys = reversed(sorted_keys)

        for key in sorted_keys:
            row_ids = index.storage[key]

            for row_id in row_ids:

                if self.query_state.filters:
                    if Matcher.matches(self.query_state.table_rows[row_id], self.query_state.filters):
                        row = self.query_state.table_rows[row_id].copy()
                        row["row_id"] = row_id
                        result.append(row)
                else:
                    row = self.query_state.table_rows[row_id].copy()
                    row["row_id"] = row_id
                    result.append(row)

                if target_count is not None and len(result) >= target_count:
                    break

            if target_count is not None and len(result) >= target_count:
                break

        return result

    def _apply_ordering(self, items: list) -> list:
        if self.query_state.order_by:
            order_by_field = self.query_state.order_by[0]
            order_by_type = self.query_state.order_by[1]

            if items and order_by_field not in items[0]:
                raise KeyNotExist(f"Key '{order_by_field}' not exists")

            if order_by_type == "desc":
                items = sorted(items, key=lambda x: x[order_by_field], reverse=True)
            else:
                items = sorted(items, key=lambda x: x[order_by_field])

        return items

    def _apply_offset(self, items: list) -> list:
        if self.query_state.offset is not None:
            items = items[self.query_state.offset:]
        return items

    def _apply_limit(self, items: list) -> list:
        if self.query_state.limit is not None:
            items = items[:self.query_state.limit]
        return items

    def _apply_select(self, items: list) -> list:
        if len(self.query_state.selected_fields) != 0:
            items = [
                {key:item.get(key) for key in self.query_state.selected_fields if item.get(key) is not None}
                for item in items
            ]

        return [item for item in items if item]

    def _apply_join(self, items: list) -> list:
        other_table, join_items = next(iter(self.query_state.join.items()))

        left_filed, right_field = join_items

        result = []

        for item in items:
            for row in other_table._rows.values():

                if item.get(left_filed) is not None and row.get(right_field) is not None:
                    if item[left_filed] == row[right_field]:
                        merged = QueryExecutor._merge_two_rows(item, row)
                        result.append(merged)

        return result

    def _choice_func(self, func_name: str):
        funcs = {
            "finder": self.finder,
            "index_scan": self._index_scan,
            "join": self._apply_join,
            "order_by": self._apply_ordering,
            "limit": self._apply_limit,
            "offset": self._apply_offset,
            "select": self._apply_select
        }

        result = funcs[func_name]
        return result

    @timer
    def run_plan(self, plan: list) -> list:
        result = None

        for step in plan:
            func = self._choice_func(step)

            if result is None:
                result = func()
            else:
                result = func(result)

        return result