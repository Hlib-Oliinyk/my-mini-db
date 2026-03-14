from mini_db.database import Database


db = Database()

users = db.create_table("users")

users.insert({"name":"Hlib", "age": 20})
users.insert({"name":"Glib", "age": 22})
users.insert({"name":"Hlib", "age": 17})


users.create_index("age", index_type="range")
# users.create_index("name", index_type="hash")
# users.create_index(("name", "age"), index_type="composite")

posts = db.create_table("posts")

posts.insert({"post_name": "First post", "author_id": 1})
posts.insert({"post_name": "Nice post", "author_id": 2})

index = users._indexes["age"]

print(index.storage)

# for i in users._indexes.values():
#     print(i.storage)

# users.query().update({"name":"Hlib"}, {"name":"Glib"})
# users.insert({"name":"Hlib", "age": 20})


print(index.storage)
# for i in users._indexes.values():
#     print(i.storage)

x = users.query()._query_executor

y = users.query().filter(name="Hlib")._query_executor