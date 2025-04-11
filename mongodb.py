from decouple import config
from pymongo import MongoClient

mongo_uri = config("MONGO_URI")
db_name = config("DB_NAME")
collection_name = config("COLLECTION_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]
