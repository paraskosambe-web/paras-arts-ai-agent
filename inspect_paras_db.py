import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")

client = MongoClient(MONGO_URI)

db = client["test"]

print("Connected to Paras Arts database!")
print("\nCollections:")

for collection_name in db.list_collection_names():
    print("-", collection_name)

client.close()