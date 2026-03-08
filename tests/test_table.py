import pytest

from mini_db.database import Database
from mini_db.table import Table
from mini_db.exceptions import TableExists


@pytest.fixture
def db():
    return Database()


def test_create_table(db):
    users = db.create_table("users")
    assert isinstance(users, Table)


def test_create_exist_table(db):
    table_name = "users"
    db.create_table(table_name)

    with pytest.raises(TableExists):
        db.create_table(table_name)


def test_get_table(db):
    table_name = "users"
    db.create_table(table_name)

    users_table = db.get_table("users")
    assert isinstance(users_table, Table)


def test_get_not_exist_table(db):
    table_name = "users"
    users_table = db.get_table(table_name)

    assert users_table is None


def test_drop_table(db):
    table_name = "users"
    db.create_table(table_name)

    user_table = db.get_table("users")

    assert isinstance(user_table, Table)
    assert db.drop_table(table_name) == True


def test_drop_not_exist_table(db):
    assert db.drop_table("users") is None


def test_insert(db):
    table_name = "users"
    users = db.create_table(table_name)

    assert users.insert({"name":"Hlib"}) == 1


def test_bulk_insert(db):
    table_name = "users"
    users = db.create_table(table_name)

    for _ in range(10):
        users.insert({"name":"Hlib"})

    assert len(users._rows) == 10


def test_get_row(db):
    table_name = "users"
    data = {"name":"Hlib"}

    users = db.create_table(table_name)
    users.insert(data)

    assert users.get(1) == data


def test_get_not_exist_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    assert users.get(1) is None


def test_update_row_by_id(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib"})
    updated_user = users.update(1, {"name":"Glib"})

    assert updated_user == 1
    assert users._rows.get(1)["name"] == "Glib"


def test_update_row_by_value(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib"})
    updated_user = users.query().update({"name":"Hlib"}, {"name":"Glib"})

    assert updated_user == 1
    assert users._rows.get(1)["name"] == "Glib"


def test_bulk_update_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    for _ in range(10):
        users.insert({"name":"Hlib"})

    updated_users = users.query().update({"name":"Hlib"}, {"name":"Glib"})

    assert updated_users == 10


def test_update_not_exist_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    updated_user = users.query().update({"name":"Hlib"}, {"name":"Glib"})

    assert updated_user == 0


def test_delete_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib"})

    assert users.delete(1) == True


def test_delete_not_exist_row(db):
    table_name = "users"
    users = db.create_table(table_name)

    assert users.delete(1) == False