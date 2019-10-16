import pymongo
from datetime import date

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = '27017'
DB_NAME = 'movie_recommendation'

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]

def get_today_query_table():
    today = date.today()
    return db[str(today) + "_query_table"]

def get_former_query_table(date):
    return db[str(date) + "_query_table"]

def get_daily_summary_watch_table(date):
    return db[str(date) + '_watch_data']
