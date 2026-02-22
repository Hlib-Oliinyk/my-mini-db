from mini_db.database import Database


db = Database()

users = db.create_table("users")

users.insert({"name":"Hlib5", "age": 22})
users.insert({"name":"Hlib1", "age": 18})
users.insert({"name":"Hlib4", "age": 21})
users.insert({"name":"Hlib2", "age": 19})
users.insert({"name":"Hlib3", "age": 20})


print(users.query().get(id=1))
print(users.query().order_by("name").all())