import pytest

from mini_db.database import Database


@pytest.fixture
def db():
    return Database()


def test_add_composite_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index(("name", "age"), "composite")

    users.insert({"name":"Hlib1", "age": 18})
    users.insert({"name":"Hlib2", "age": 19})

    index = users._indexes[("name", "age")]

    assert index.storage == {("Hlib1", 18): {1}, ("Hlib2", 19): {2}}


def test_update_with_composite_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index(("name", "age"), "composite")

    users.insert({"name":"Hlib1", "age": 18})
    users.insert({"name":"Hlib2", "age": 19})

    index = users._indexes[("name", "age")]
    assert index.storage == {("Hlib1", 18): {1}, ("Hlib2", 19): {2}}

    users.query().update({"age": 18}, {"age": 20})
    assert index.storage == {("Hlib1", 20): {1}, ("Hlib2", 19): {2}}


def test_composite_index_remove(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index(("name", "age"), "composite")

    users.insert({"name":"Hlib1", "age": 18})
    users.insert({"name":"Hlib2", "age": 19})

    index = users._indexes[("name", "age")]
    assert len(index.storage) == 2

    index.remove(1, ("Hlib1", 18))
    assert len(index.storage) == 1


def test_composite_index_find(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index(("name", "age"), "composite")

    users.insert({"name":"Hlib", "age": 18})

    index = users._indexes[("name", "age")]

    find_eq = index.find("eq", ("Hlib",18))
    find_gt = index.find("gt", ("Hlib",19))
    find_not_exist = index.find("eq", ("Hlib", 100))
    assert find_eq == {1}
    assert find_gt is None
    assert find_not_exist == set()


def test_composite_index_insert(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index(("name", "age"), "composite")

    index = users._indexes[("name", "age")]
    assert len(index.storage) == 0

    users.insert({"name": "Hlib", "age": 18})
    assert index.storage == {("Hlib", 18): {1}}


def test_composite_index_delete_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib2", "age": 19})

    users.create_index(("name", "age"), "composite")

    index = users._indexes[("name", "age")]
    assert len(index.storage) == 2

    users.delete(1)
    assert index.storage == {("Hlib2", 19): {2}}


def test_composite_index_update(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.create_index(("name", "age"), "composite")

    index = users._indexes[("name", "age")]
    assert index.storage == {("Hlib", 18): {1}}

    users.query().update({"name":"Hlib", "age":18}, {"name": "Glib", "age": 21})
    assert index.storage == {("Glib", 21): {1}}


def test_duplicate_composite_keys(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.insert({"name": "Hlib", "age": 18})
    users.insert({"name": "Hlib", "age": 18})
    users.create_index(("name", "age"), "composite")

    index = users._indexes[("name", "age")]
    assert index.storage == {("Hlib", 18): {1, 2, 3}}


def test_update_one_field(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.create_index(("name", "age"), "composite")

    index = users._indexes[("name", "age")]
    assert index.storage == {("Hlib", 18): {1}}

    users.query().update({"name": "Hlib"}, {"name": "Glib"})
    assert index.storage == {("Glib", 18): {1}}


def test_composite_index_delete_all_rows(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.insert({"name": "Hlib", "age": 18})

    users.create_index(("name", "age"), "composite")

    index = users._indexes[("name", "age")]
    assert index.storage == {("Hlib", 18): {1,2}}

    users.delete(1)
    users.delete(2)
    assert index.storage == {}


def test_composite_index_partial_update(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.insert({"name": "Hlib", "age": 18})

    users.create_index(("name", "age"), "composite")

    index = users._indexes[("name", "age")]
    assert index.storage == {("Hlib", 18): {1,2}}

    users.query().update({"age": 18}, {"age": 20})
    assert index.storage == {("Hlib", 20): {1,2}}


def test_composite_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib5", "age": 8})
    users.insert({"name": "Hlib3", "age": 16})
    users.insert({"name": "Hlib1", "age": 44})
    users.insert({"name": "Hlib9", "age": 16})
    users.insert({"name": "Hlib7", "age": 16})

    users.create_index(("name", "age"), "composite")

    users.query().update({"age": 16}, {"age": 28})

    users.delete(1)
    users.delete(2)

    index = users._indexes[("name", "age")]
    assert index.storage == {("Hlib1", 44): {3}, ("Hlib9", 28): {4}, ("Hlib7", 28): {5}}