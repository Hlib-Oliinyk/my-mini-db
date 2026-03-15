from mini_db.database import Database


database = Database()

users = database.create_table("users")
users.insert({"name": "Hlib", "age": 18})
users.insert({"name": "Max", "age": 19})

# Create hash index
users.create_index("name", "hash")

# Create range index
users.create_index("age", "range")

# Create composite index
users.create_index(("name", "age"), "composite")

# Remove index
users.remove_index("name")