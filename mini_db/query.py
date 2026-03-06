from copy import deepcopy

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

        return query

    def _get_candidate_ids(self, filters: list) -> set[int]:
        candidate_ids = set()
        indexes_find_value = {}

        used_index = False

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
        new_query._filters.append(kwargs)
        return new_query

    def limit(self, limit_num: int):
        new_query = self._clone_query()
        new_query._limit = limit_num
        return new_query

    def order_by(self, order_field: str, order_type: str | None = None):
        new_query = self._clone_query()
        new_query._order_by = (order_field, order_type)
        return new_query

    def offset(self, offset_num: int):
        new_query = self._clone_query()
        new_query._offset = offset_num
        return new_query

    def _finder(self) -> list:
        result = []
        candidate_ids = self._get_candidate_ids(self._filters)

        for row_id in candidate_ids:
            row = self._table._rows[row_id]
            if Matcher._matches(row, self._filters):
                row["row_id"] = row_id
                result.append(row)

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
        sorted_items = []
        find_ids = set(row["row_id"] for row in items)

        target_count = self._count_targets()

        if self._order_by:
            order_by_field = self._order_by[0]
            order_by_type = self._order_by[1]

            if items and order_by_field not in items[0]:
                raise KeyNotExist(f"Key '{order_by_field}' not exists")

            if order_by_field in self._table._indexes:
                index = self._table._indexes[order_by_field]
                sorted_keys = index.sorted_keys

                if order_by_type == "desc":
                    sorted_keys = reversed(sorted_keys)

                if isinstance(index, RangeIndex):
                    for key in sorted_keys:
                        for row_id in index.storage[key]:

                            if row_id in find_ids:
                                sorted_items.append(self._table._rows[row_id])

                                if target_count is not None and len(sorted_items) >= target_count:
                                    break

                        if target_count is not None and len(sorted_items) >= target_count:
                            break

                    items = sorted_items
            else:
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

    def _build_plan(self) -> list:
        plan = []

        plan.append("finder")

        if self._order_by:
            plan.append("order_by")
        if self._offset is not None:
            plan.append("offset")
        if self._limit is not None:
            plan.append("limit")

        return plan

    def _run_plan(self, plan: list) -> list:
        result = None

        for step in plan:
            if step == "finder":
                result = self._finder()
            elif step == "order_by":
                result = self._apply_ordering(result)
            elif step == "offset":
                result = self._apply_offset(result)
            elif step == "limit":
                result = self._apply_limit(result)

        return result

    @timer
    def _execute(self) -> list:
        plan = self._build_plan()
        result = self._run_plan(plan)
        return result

    def all(self) -> list:
        return self._execute()

    def first(self) -> dict | None:
        result = self._execute()
        return result[0] if result else None

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