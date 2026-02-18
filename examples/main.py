from mini_db.table import Table

users = Table("users")

users.insert({"name":"Hlib", "age":18})
users.insert({"name":"Hlib", "age":21})
users.insert({"name":"Hlib", "age":15})

print(users.query().filter(name="Hlib", age__gt=16).all())