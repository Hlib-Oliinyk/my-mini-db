from copy import deepcopy

from .indexes.composite_index import CompositeIndex
from .indexes.range_index import RangeIndex
from .matcher import Matcher
from .exceptions import KeyNotExist, RowNotExists, MultipleObjectReturn
from .utils import timer


class Query:
    def __init__(self, table):
        self._table = table
        self._filters: list[dict] = []
        self._limit: int | None = None
        self._order_by: (str | None, str | None) = None
        self._offset: int | None = None
        self._selected_fields: list[tuple] = []
        self._join: dict = {}

    @staticmethod
    def _merge_two_rows(row_one: dict, row_two: dict) -> dict:
        merged = row_one.copy()

        for key, value in row_two.items():
            merged[key] = value

        return merged

    @staticmethod
    def _clone_row(row_id: int, row_value: dict) -> dict:
        new_row = {}

        new_row["id"] = row_id
        for key, value in row_value.items():
            new_row[key] = value

        return new_row

    def _clone_query(self):
        query = Query(self._table)

        query._filters = deepcopy(self._filters)
        query._limit = deepcopy(self._limit)
        query._order_by = deepcopy(self._order_by)
        query._offset = deepcopy(self._offset)
        query._selected_fields = deepcopy(self._selected_fields)
        query._join = deepcopy(self._join)

        return query

    def _get_candidate_ids(self, filters: list) -> set[int]:
        candidate_ids = set()
        indexes_find_value = {}
        used_index = False
        filter_map = Matcher._filter_map(filters)

        for index_field, index in self._table._indexes.items():

            if isinstance(index, CompositeIndex):
                if all(key in filter_map for key in index_field):

                    value = tuple(filter_map.get(field) for field in index_field)
                    find = index.find("eq", value)
                    return find

        for _filter in filters:
            operator, field, value = Matcher._match_operators(_filter)

            if field in self._table._indexes:
                index = self._table._indexes[field]
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
            return set(self._table._rows.keys())

    def filter(self, **kwargs):
        new_query = self._clone_query()

        for key, value in kwargs.items():
            new_filter = {key:value}
            new_query._filters.append(new_filter)

        return new_query

    def limit(self, limit_num: int):
        new_query = self._clone_query()

        if limit_num < 0:
            limit_num = -limit_num

        new_query._limit = limit_num
        return new_query

    def order_by(self, order_field: str, order_type: str | None = None):
        new_query = self._clone_query()
        new_query._order_by = (order_field, order_type)
        return new_query

    def offset(self, offset_num: int):
        new_query = self._clone_query()

        if offset_num < 0:
            offset_num = -offset_num

        new_query._offset = offset_num
        return new_query

    def select(self, *args):
        new_query = self._clone_query()
        for arg in args:
            new_query._selected_fields.append(arg)
        return new_query

    def join(self, other_table, on: tuple):
        new_query = self._clone_query()
        new_query._join[other_table] = on
        return new_query

    def _finder(self) -> list:
        result = []
        candidate_ids = self._get_candidate_ids(self._filters)

        for row_id in candidate_ids:
            row = self._table._rows[row_id].copy()

            if Matcher._matches(row, self._filters):
                row["row_id"] = row_id
                result.append(row)

        return result

    def _index_scan(self):
        result = []
        target_count = self._count_targets()

        index = self._table._indexes[self._order_by[0]]
        sorted_keys = index.sorted_keys

        if self._order_by[1] == "desc":
            sorted_keys = reversed(sorted_keys)

        for key in sorted_keys:
            row_ids = index.storage[key]

            for row_id in row_ids:

                if self._filters:
                    if Matcher._matches(self._table._rows[row_id], self._filters):
                        row = self._table._rows[row_id].copy()
                        row["row_id"] = row_id
                        result.append(row)
                else:
                    row = self._table._rows[row_id].copy()
                    row["row_id"] = row_id
                    result.append(row)

                if target_count is not None and len(result) >= target_count:
                    break

            if target_count is not None and len(result) >= target_count:
                break

        return result

    def _count_targets(self) -> int:
        target_count = None

        if self._limit is not None:
            if self._offset is not None:
                target_count = self._limit + self._offset
            else:
                target_count = self._limit

        return target_count

    def _apply_ordering(self, items: list) -> list:
        if self._order_by:
            order_by_field = self._order_by[0]
            order_by_type = self._order_by[1]

            if items and order_by_field not in items[0]:
                raise KeyNotExist(f"Key '{order_by_field}' not exists")

            if order_by_type == "desc":
                items = sorted(items, key=lambda x: x[order_by_field], reverse=True)
            else:
                items = sorted(items, key=lambda x: x[order_by_field])

        return items

    def _apply_offset(self, items: list) -> list:
        if self._offset is not None:
            items = items[self._offset:]
        return items

    def _apply_limit(self, items: list) -> list:
        if self._limit is not None:
            items = items[:self._limit]
        return items

    def _apply_select(self, items: list) -> list:
        if len(self._selected_fields) != 0:
            if len(self._selected_fields) == 1 and not all(
                    [item.get(key) for key in self._selected_fields if item.get(key) is not None]
                    for item in items):
                return []

            items = [{key:item.get(key) for key in self._selected_fields if item.get(key) is not None}
                  for item in items]

        return items

    def _apply_join(self, items: list) -> list:
        other_table, join_items = next(iter(self._join.items()))

        left_filed, right_field = join_items

        result = []

        for item in items:
            for row in other_table._rows.values():

                if item.get(left_filed) is not None and row.get(right_field) is not None:
                    if item[left_filed] == row[right_field]:
                        merged = Query._merge_two_rows(item, row)
                        result.append(merged)

        return result

    def _choice_func(self, func_name: str):
        funcs = {
            "finder": self._finder,
            "index_scan": self._index_scan,
            "join": self._apply_join,
            "order_by": self._apply_ordering,
            "limit": self._apply_limit,
            "offset": self._apply_offset,
            "select": self._apply_select
        }

        result = funcs[func_name]
        return result

    def _build_plan(self) -> list:
        plan = []

        plan.append("finder")

        if len(self._join) != 0:
            plan.append("join")

        if self._order_by:
            order_by_filed = self._order_by[0]

            if order_by_filed in self._table._indexes:
                index = self._table._indexes[order_by_filed]

                if isinstance(index, RangeIndex):
                    plan.remove("finder")
                    plan.insert(0, "index_scan")
            else:
                plan.append("order_by")

        if self._offset is not None:
            plan.append("offset")
        if self._limit is not None:
            plan.append("limit")
        if len(self._selected_fields) != 0:
            plan.append("select")

        return plan

    def _run_plan(self, plan: list) -> list:
        result = None

        for step in plan:
            func = self._choice_func(step)

            if result is None:
                result = func()
            else:
                result = func(result)

        return result

    @timer
    def _execute(self) -> list:
        plan = self._build_plan()
        print(plan)
        result = self._run_plan(plan)
        return result

    def all(self) -> list:
        return self._execute()

    def first(self) -> dict | None:
        result = self._execute()
        return result[0] if result else None

    def explain(self) -> list:
        build_plan = self._build_plan()
        return build_plan

    def count(self) -> int:
        return len(self._finder())

    def exists(self) -> bool:
        if self._finder():
            return True
        return False

    def get(self, **kwargs) -> dict | None:
        new_query = self._clone_query()
        new_query._filters.append(kwargs)

        result = new_query._finder()

        if len(result) == 0:
            raise RowNotExists()
        if len(result) > 1:
            raise MultipleObjectReturn()

        return result[0]

    def update(self, filters: dict, values: dict) -> int:
        matching_ids = []
        candidate_ids = self._get_candidate_ids([filters])

        for row_id in candidate_ids:
            row = self._table._rows[row_id]
            if Matcher._matches(row, [filters]):
                matching_ids.append(row_id)

        for row_id in matching_ids:
            self._table.update(row_id, values)

        return len(matching_ids)