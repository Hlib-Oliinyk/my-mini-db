from typing import Any

from mini_db.indexes.range_index import RangeIndex


def build_execution_plan(query_state: Any) -> list:
    plan = list()
    plan.append("finder")

    if len(query_state.join) != 0:
        plan.append("join")

    if query_state.order_by:
        order_by_filed = query_state.order_by[0]

        if order_by_filed in query_state.table_indexes:
            index = query_state.table_indexes[order_by_filed]

            if isinstance(index, RangeIndex):
                plan.remove("finder")
                plan.insert(0, "index_scan")
        else:
            plan.append("order_by")

    if query_state.offset is not None:
        plan.append("offset")
    if query_state.limit is not None:
        plan.append("limit")
    if len(query_state.selected_fields) != 0:
        plan.append("select")

    return plan