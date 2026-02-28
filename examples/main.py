from mini_db.database import Database


db = Database()

users = db.create_table("users")

users.insert({"name":"Hlib", "age": 22})
users.insert({"name":"Hlib", "age": 18})
users.insert({"name":"Hlib1", "age": 21})
users.insert({"name":"Hlib2", "age": 19})
users.insert({"name":"Hlib3", "age": 20})

users.create_index("age", index_type="range")

for i in users._indexes.values():
    print(i.storage)

users.query().update({"name":"Hlib"}, {"name":"Glib"})

for i in users._indexes.values():
    print(i.storage)

print(users.query().filter(age__gt=20).all())