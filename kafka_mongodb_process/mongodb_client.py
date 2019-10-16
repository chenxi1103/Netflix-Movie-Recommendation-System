#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-10-12
import pymongo
from datetime import date

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = '27017'
DB_NAME = 'movie_recommendation'
WATCH_TABLE_NAME = 'stream_watch_data'
RATE_TABLE_NAME = 'stream_rate_data'
USER_TABLE_NAME = 'user_data'
MOVIE_TABLE_NAME = 'movie_data'
WATCH_DAILY_SUMMARY_TABLE_NAME = str(date.today()) + '_watch_data'

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]

def get_movie_table():
    return db[MOVIE_TABLE_NAME]

def get_user_table():
    return db[USER_TABLE_NAME]

def get_watch_table():
    return db[WATCH_TABLE_NAME]

def get_rate_table():
    return db[RATE_TABLE_NAME]

def get_daily_watch_table():
    return db[WATCH_DAILY_SUMMARY_TABLE_NAME]

def get_daily_summary_watch_table(date):
    return db[date + '_watch_data']
