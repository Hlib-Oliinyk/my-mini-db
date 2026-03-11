import pytest

from mini_db.database import Database
from mini_db.exceptions import RowNotExists, MultipleObjectReturn, KeyNotExist


@pytest.fixture
def db():
    return Database()


def test_all(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib"})
    users.insert({"name":"Glib"})
    all_users = users.query().all()

    assert isinstance(all_users, list)
    assert len(all_users) == 2


def test_all_with_empty_table(db):
    table_name = "users"
    users = db.create_table(table_name)

    all_users = users.query().all()
    assert len(all_users) == 0


def test_first(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib"})
    users.insert({"name":"Glib"})
    user = users.query().first()

    assert isinstance(user, dict)
    assert user == {"name":"Hlib","row_id": 1}


def test_first_with_empty_table(db):
    table_name = "users"
    users = db.create_table(table_name)

    user = users.query().first()
    assert user is None


def test_count(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name":"Hlib"})
    users.insert({"name":"Hlib"})
    users.insert({"name":"Hlib"})

    users_count = users.query().filter(name="Hlib").count()

    assert users_count == 3


def test_exists(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib"})
    users.insert({"name": "Hlib"})
    users.insert({"name": "Hlib"})

    users_exists = users.query().filter(name="Hlib").exists()

    assert users_exists == True


def test_get(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib"})

    get_user = users.query().get(name="Hlib")

    assert isinstance(get_user, dict)
    assert get_user == {"name": "Hlib", "row_id": 1}


def test_get_not_exist(db):
    table_name = "users"
    users = db.create_table(table_name)

    with pytest.raises(RowNotExists):
        users.query().get(name="Hlib")


def test_get_multiple_object(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib"})
    users.insert({"name": "Hlib"})

    with pytest.raises(MultipleObjectReturn):
        users.query().get(name="Hlib")


def test_query_with_filter(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.insert({"name": "Hlib", "age": 19})

    user = users.query().filter(name="Hlib").all()

    assert user[0] == {"name": "Hlib", "age": 18, "row_id": 1}


def test_query_with_not_exist_filter(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})

    user = users.query().filter(height=100).all()

    assert len(user) == 0


def test_query_with_limit(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib", "age": 18})
    users.insert({"name": "Hlib", "age": 19})

    user = users.query().limit(1).all()

    assert len(user) == 1


def test_query_with_order_by(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 19})
    users.insert({"name": "Hlib2", "age": 18})

    order_by_age = users.query().order_by("age").all()
    order_by_name = users.query().order_by("name").all()
    order_by_desc = users.query().order_by("age", "desc").all()

    assert order_by_age[0] == {"name": "Hlib2", "age": 18, "row_id": 2}
    assert order_by_name[0] == {"name": "Hlib1", "age": 19, "row_id": 1}
    assert order_by_desc[0] == {"name": "Hlib1", "age": 19, "row_id": 1}

    with pytest.raises(KeyNotExist):
        users.query().order_by("height").all()


def test_query_with_offset(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 19})
    users.insert({"name": "Hlib2", "age": 18})

    user = users.query().offset(1).all()
    big_offset = users.query().offset(3).all()

    assert user[0] == {"name": "Hlib2", "age": 18, "row_id": 2}
    assert len(big_offset) == 0


def test_query_with_many_operations(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 19})
    users.insert({"name": "Hlib2", "age": 18})
    users.insert({"name": "Hlib4", "age": 22})
    users.insert({"name": "Hlib3", "age": 7})

    result = users.query().filter(name__contains="ib").order_by("age").limit(2).offset(1).all()

    assert result[1] == {"name": "Hlib1", "age": 19, "row_id": 1}


def test_query_with_different_operations_order(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 19})
    users.insert({"name": "Hlib2", "age": 18})
    users.insert({"name": "Hlib4", "age": 22})
    users.insert({"name": "Hlib3", "age": 7})

    test1 = users.query().filter(name__contains="ib").order_by("age").limit(2).offset(1).all()
    test2 = users.query().order_by("age").offset(1).filter(name__contains="ib").limit(2).all()

    assert test1 == test2


def test_select(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 19})
    users.insert({"name": "Hlib2", "age": 18})

    select_query = users.query().select("name", "age").all()
    assert select_query == [{"name":"Hlib1", "age": 19}, {"name":"Hlib2", "age": 18}]


def test_select_with_not_exist_key(db):
    table_name = "users"
    users = db.create_table(table_name)

    users.insert({"name": "Hlib1", "age": 19})
    users.insert({"name": "Hlib2", "age": 18})

    select_query1 = users.query().select("name", "age", "size").all()
    select_query2 = users.query().select("size").all()
    assert select_query1 == [{"name":"Hlib1", "age": 19}, {"name":"Hlib2", "age": 18}]
    assert select_query2 == []