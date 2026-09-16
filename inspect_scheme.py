import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")

client = MongoClient(MONGO_URI)

db = client["test"]

for collection_name in ["orders", "artworks", "services", "faqs"]:

    print("\n" + "=" * 60)
    print(f"COLLECTION: {collection_name}")
    print("=" * 60)

    document = db[collection_name].find_one(
        {},
        {"_id": 0}
    )

    if document:
        print(document)
    else:
        print("No documents found.")

client.close()