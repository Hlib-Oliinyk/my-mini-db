from mini_db.database import Database


# Create database and table
database = Database()
users = database.create_table("users")

# Insert a row
users.insert({"name": "Hlib", "age": 18})

# Get by id
users.get(1)

# Update by id
users.update(1, {"age": 19})

# Delete by id
users.delete(1)

# Get table by table name
database.get_table("users")

# Drop table by table name
database.drop_table("users")