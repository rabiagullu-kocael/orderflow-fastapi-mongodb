import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
print("Mongo URL:", MONGODB_URL)  

client = MongoClient(MONGODB_URL)
db = client["orderflow_db"]


