from mini_db.database import Database


database = Database()

users = database.create_table("users")
users.insert({"name": "Hlib", "age": 18})
users.insert({"name": "Max", "age": 19})

posts = database.create_table("posts")
posts.insert({"post_name": "First post", "author_id": 1})

# Get all records from table
result_all = users.query().all()

# Get first (one) record from table
result_first = users.query().first()

# Select output field
result_select = users.query().select("name").all()

# Filter by filed
result_field = users.query().filter(name="Hlib").all()

# Order by value
result_orderBy = users.query().order_by("age").all()

# Order by value (DESC)
result_orderBy_desc = users.query().order_by("age", "desc").all()

# Limit
result_limit = users.query().limit(2).all()

# Offset
result_offset = users.query().offset(1).all()

# Add inner join
result_join = users.query().join(posts, on=("row_id", "author_id")).all()

# Combined query
result = users.query().select("name").filter(age__gt=17).order_by("age").limit(1).all()