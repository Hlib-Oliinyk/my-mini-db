import pytest

from mini_db.database import Database
from mini_db.exceptions import IndexAlreadyExists


@pytest.fixture
def db():
    return Database()


def test_add_hash_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib"})
    users.insert({"name":"Glib"})

    users.create_index("name", "hash")

    index = users._indexes["name"]
    assert index.storage == {"Hlib": {1}, "Glib": {2}}


def test_add_hash_index_to_field_with_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index("name", "hash")

    with pytest.raises(IndexAlreadyExists):
        users.create_index("name", "range")


def test_update_with_hash_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib"})
    users.create_index("name", "hash")

    index = users._indexes["name"]
    assert index.storage == {"Hlib": {1}}

    users.query().update({"name":"Hlib"}, {"name":"Glib"})
    assert index.storage == {"Glib": {1}}


def test_remove_hash_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index("name", "hash")
    assert len(users._indexes) == 1

    users.remove_index("name")
    assert len(users._indexes) == 0


def test_hash_index_remove(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib2", "age": 19})
    users.create_index("name", "hash")

    index = users._indexes["name"]
    assert len(index.storage) == 2

    index.remove(1, "Hlib1")
    assert len(index.storage) == 1


def test_hash_index_find(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.insert({"name": "Hlib", "age": 19})
    users.create_index("name", "hash")

    index = users._indexes["name"]
    find_eq = index.find("eq", "Hlib")
    find_gt = index.find("gt", 19)
    find_not_exist = index.find("eq", "Hlib1")

    assert find_eq == {1, 2}
    assert find_gt is None
    assert find_not_exist == set()


def test_hash_index_insert(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib"})
    users.create_index("name", "hash")

    index = users._indexes["name"]
    assert index.storage == {"Hlib": {1}}

    users.insert({"name": "Hlib"})
    assert index.storage == {"Hlib": {1, 2}}


def test_hash_index_delete_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1"})
    users.insert({"name": "Hlib2"})
    users.create_index("name", "hash")

    index = users._indexes["name"]
    assert index.storage == {"Hlib1": {1}, "Hlib2": {2}}

    users.delete(1)
    assert index.storage == {"Hlib2": {2}}


def test_hash_index_update(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1"})
    users.create_index("name", "hash")

    index = users._indexes["name"]
    assert index.storage == {"Hlib1": {1}}

    users.query().update({"name":"Hlib1"}, {"name": "Hlib1"})
    assert index.storage == {"Hlib1": {1}}


def test_hash_index_delete_all_rows(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib"})
    users.insert({"name": "Hlib"})
    users.create_index("name", "hash")

    index = users._indexes["name"]
    assert index.storage == {"Hlib": {1, 2}}

    users.delete(1)
    users.delete(2)

    assert len(index.storage) == 0


def test_hash_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index("name", "hash")

    users.insert({"name": "Hlib1"})
    users.insert({"name": "Hlib2"})
    users.insert({"name": "Hlib1"})
    users.insert({"name": "Hli4"})
    users.insert({"name": "Hlib1"})
    users.insert({"name": "Hlib2"})
    users.insert({"name": "Hlib9"})

    users.query().update({"name": "Hlib1"}, {"name": "Glib"})
    users.delete(2)
    users.delete(4)
    users.delete(5)

    index = users._indexes["name"]
    assert index.storage == {"Glib": {1,3}, "Hlib2": {6}, "Hlib9": {7}}


def test_add_range_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib1", "age": 19})
    users.insert({"name":"Hlib2", "age": 18})

    users.create_index("age", "range")

    index = users._indexes["age"]
    assert index.storage == {19: {1}, 18: {2}}
    assert index.sorted_keys == [18, 19]


def test_update_with_range_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.create_index("age", "range")

    index = users._indexes["age"]
    assert index.storage == {18: {1}}

    users.query().update({"age":18}, {"age":19})
    assert index.storage == {19: {1}}


def test_range_index_remove(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib2", "age": 19})
    users.create_index("age", "range")

    index = users._indexes["age"]
    assert len(index.storage) == 2
    assert index.sorted_keys == [18, 19]

    index.remove(1, 18)
    assert len(index.storage) == 1
    assert index.sorted_keys == [19]


def test_range_index_find(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib2", "age": 19})
    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib4", "age": 22})
    users.insert({"name": "Hlib3", "age": 21})
    users.create_index("age", "range")

    index = users._indexes["age"]
    find_eq = index.find("eq", 19)
    find_gt = index.find("gt", 20)
    find_not_exist = index.find("eq", 100)
    find_edge_case = index.find("gt", 100)

    assert find_eq == {1}
    assert find_gt == {3,4}
    assert find_not_exist == set()
    assert find_edge_case == set()


def test_range_index_insert(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 18})
    users.create_index("age", "range")

    index = users._indexes["age"]
    assert index.storage == {18: {1}}
    assert index.sorted_keys == [18]

    users.insert({"name": "Hlib2", "age": 17})
    assert index.storage == {18: {1}, 17: {2}}
    assert index.sorted_keys == [17, 18]

    users.insert({"name": "Hlib3", "age": 18})
    assert index.storage == {18: {1, 3}, 17: {2}}
    assert index.sorted_keys == [17, 18]


def test_range_index_delete_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib2", "age": 17})
    users.create_index("age", "range")

    index = users._indexes["age"]
    assert index.storage == {18: {1}, 17: {2}}

    users.delete(1)
    assert index.storage == {17: {2}}


def test_range_index_update_sorted_keys(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index("age", "range")

    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib2", "age": 14})

    index = users._indexes["age"]
    assert index.sorted_keys == [14, 18]

    users.query().update({"age": 14}, {"age": 20})
    assert index.sorted_keys == [18, 20]


def test_range_index_duplicate_values(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index("age", "range")

    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib2", "age": 18})
    users.insert({"name": "Hlib3", "age": 18})

    index = users._indexes["age"]
    assert index.storage == {18: {1, 2, 3}}


def test_range_index(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.create_index("age", "range")

    users.insert({"name": "Hlib1", "age": 18})
    users.insert({"name": "Hlib5", "age": 14})
    users.insert({"name": "Hlib2", "age": 12})
    users.insert({"name": "Hlib7", "age": 18})
    users.insert({"name": "Hlib8", "age": 19})
    users.insert({"name": "Hlib11", "age": 21})

    users.query().update({"age": 18}, {"age": 20})
    users.delete(2)
    users.delete(4)
    users.delete(5)

    index = users._indexes["age"]
    assert index.storage == {12: {3} ,20: {1}, 21: {6}}
    assert index.sorted_keys == [12, 20, 21]