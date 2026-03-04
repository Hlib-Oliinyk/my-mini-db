from mini_db.database import Database


db = Database()

users = db.create_table("users")

users.insert({"name":"Hlib", "age": 20})
users.insert({"name":"Hlib", "age": 19})
users.insert({"name":"Hlib", "age": 22})
users.insert({"name":"Hlib1", "age": 18})
users.insert({"name":"Hlib2", "age": 21})

# users.create_index("age", index_type="range")
users.create_index("name", index_type="hash")

# for i in users._indexes.values():
#     print(i.storage)
#
# users.query().update({"name":"Hlib"}, {"name":"Glib"})
#
# for i in users._indexes.values():
#     print(i.storage)

print(users.query().filter(age__gt=19).order_by("age").limit(2).offset(1).all())