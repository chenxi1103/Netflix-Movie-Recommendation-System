#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-11-24
import pymongo

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = '27017'
DB_NAME = 'movie_recommend'
RATE_TABLE_NAME = 'rate_data'
BETA_RECOMMEND = 'beta_recommend'
ALPHA_RECOMMEND = 'alpha_recommend'
CHARLIE_RECOMMEND = 'charlie_recommend'

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]
def get_db():
    return db

def get_rate_table():
    return db[RATE_TABLE_NAME]

def get_beta_table():
    return db[BETA_RECOMMEND]

def get_alpha_table():
    return db[ALPHA_RECOMMEND]

def get_charlie_table():
    return db[CHARLIE_RECOMMEND]