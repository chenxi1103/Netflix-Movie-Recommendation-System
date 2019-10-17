import pymongo
from datetime import date, datetime, timedelta

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = '27017'
DB_NAME = 'movie_recommendation'

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]

def get_today_query_table():
    target_date = datetime.strftime(date.today() - timedelta(0), '%Y-%m-%d')
    return db["query_table_" + str(target_date)]

def get_former_query_table(date):
    return db["query_table_" + str(date)]

def get_daily_summary_watch_table(date):
    return db["watch_data_" + str(date)]
