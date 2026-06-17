import tomllib
from pymongo import MongoClient

with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

mongo_uri = secrets["MONGO_URI"]

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=30000)
client.admin.command("ping")

print("Connected successfully\n")

print("Databases:")
for db_name in client.list_database_names():
    print("-", db_name)

print("\nCollections in kayfa_student_analytics:")
db = client["kayfa_student_analytics"]

for col in db.list_collection_names():
    count = db[col].count_documents({})
    print(f"- {col}: {count}")