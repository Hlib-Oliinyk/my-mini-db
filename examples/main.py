from mini_db.database import Database


db = Database()

users = db.create_table("users")

users.insert({"name":"Hlib", "age": 22})
users.insert({"name":"Hlib", "age": 18})
users.insert({"name":"Hlib4", "age": 21})
users.insert({"name":"Hlib2", "age": 19})
users.insert({"name":"Hlib3", "age": 20})

users.create_index("name")

users.insert({"name":"Hlib3", "age": 26})

users.update({"name":"Hlib"}, {"name":"Glib"})