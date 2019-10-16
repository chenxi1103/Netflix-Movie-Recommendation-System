import pymongo
from datetime import date

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = '27017'
DB_NAME = 'movie_recommendation'

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]

def get_table():
    today = date.today()
    return db[str(today)]

def get_former_table(date):
    return db[str(date)]
