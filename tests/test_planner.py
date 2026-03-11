import pytest

from mini_db.database import Database


@pytest.fixture
def db():
    return Database()


def test_get_candidate_ids_without_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})
    users.insert({"name":"Hlib", "age": 21})

    users_query = users.query().filter(name="Hlib")
    users_query_filters = users_query._filters
    assert users_query_filters == [{"name": "Hlib"}]

    get_candidate_ids = users_query._get_candidate_ids(users_query._filters)
    assert get_candidate_ids == {1,2,3}


def test_get_candidate_ids_with_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})
    users.insert({"name":"Hlib1", "age": 21})

    users.create_index("name", "hash")

    users_query = users.query().filter(name="Hlib")
    get_candidate_ids = users_query._get_candidate_ids(users_query._filters)
    assert get_candidate_ids == {1,2}


def test_query_planner_without_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})

    users_query = users.query().filter(name="Hlib").order_by("name").offset(2).limit(1)
    query_plan = users_query._build_plan()
    assert query_plan == ["finder", "order_by", "offset", "limit"]


def test_query_planner_with_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})

    users.create_index("age", "range")

    users_query = users.query().filter(age__gt=17).order_by("age").offset(2).limit(1)
    query_plan = users_query._build_plan()
    assert query_plan == ["index_scan", "offset", "limit"]


def test_index_intersection(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})

    users.create_index("name", "hash")
    users.create_index("age", "range")

    users_query = users.query().filter(name="Hlib").filter(age__gt=18)
    get_candidate_ids = users_query._get_candidate_ids(users_query._filters)
    assert get_candidate_ids == {2}


def test_get_candidate_ids_without_match_in_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})

    users.create_index("name", "hash")

    users_query = users.query().filter(name="Hlib1")
    get_candidate_ids = users_query._get_candidate_ids(users_query._filters)
    assert get_candidate_ids == set()


def test_get_candidate_ids_full_scan(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})

    users_query = users.query().filter(age=20)
    get_candidate_ids = users_query._get_candidate_ids(users_query._filters)
    assert get_candidate_ids == {1,2}


def test_get_candidate_ids_with_composite_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})

    users.create_index(("name", "age"), "composite")

    users_query = users.query().filter(name="Hlib").filter(age=18)
    get_candidate_ids = users_query._get_candidate_ids(users_query._filters)
    assert get_candidate_ids == {1}


def test_no_match_composite_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})
    users.insert({"name":"Hlib", "age": 20})

    users.create_index(("name", "age"), "composite")

    users_query = users.query().filter(name="Hlib")
    assert users_query._get_candidate_ids(users_query._filters) == {1,2,3}


def test_build_plan(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib", "age": 18})
    users.insert({"name":"Hlib", "age": 19})

    users_query_limit = users.query().filter(name="Hlib").limit(1)
    users_query_order_by = users.query().order_by("age")
    assert users_query_limit._build_plan() == ["finder", "limit"]
    assert users_query_order_by._build_plan() == ["finder", "order_by"]