import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Get MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)

# Test connection
client.admin.command("ping")
print("✅ Connected to MongoDB Atlas!")

# Select our separate database
db = client["ai_data_agent"]

# Select collections
customers = db["customers"]
products = db["products"]
orders = db["orders"]

# Sample customers
customer_data = [
    {
        "customer_id": "C001",
        "name": "Rahul Sharma",
        "city": "Mumbai",
        "email": "rahul@example.com"
    },
    {
        "customer_id": "C002",
        "name": "Priya Patel",
        "city": "Pune",
        "email": "priya@example.com"
    },
    {
        "customer_id": "C003",
        "name": "Amit Shah",
        "city": "Mumbai",
        "email": "amit@example.com"
    }
]

# Sample products
product_data = [
    {
        "product_id": "P001",
        "name": "Laptop",
        "category": "Electronics",
        "price": 65000
    },
    {
        "product_id": "P002",
        "name": "Wireless Mouse",
        "category": "Accessories",
        "price": 1200
    },
    {
        "product_id": "P003",
        "name": "Keyboard",
        "category": "Accessories",
        "price": 2500
    }
]

# Sample orders
order_data = [
    {
        "order_id": "O001",
        "customer_id": "C001",
        "product_id": "P001",
        "quantity": 1,
        "status": "Completed"
    },
    {
        "order_id": "O002",
        "customer_id": "C002",
        "product_id": "P002",
        "quantity": 2,
        "status": "Pending"
    },
    {
        "order_id": "O003",
        "customer_id": "C003",
        "product_id": "P003",
        "quantity": 1,
        "status": "In Progress"
    }
]

# Insert sample data
customers.insert_many(customer_data)
products.insert_many(product_data)
orders.insert_many(order_data)

print("✅ Customers inserted!")
print("✅ Products inserted!")
print("✅ Orders inserted!")

# Close connection
client.close()

print("🔒 MongoDB connection closed.")