#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-10-12
import mongodb_client
from datetime import datetime, timedelta, date
movie_table = mongodb_client.get_movie_table()
user_table = mongodb_client.get_user_table()
stream_watch_table = mongodb_client.get_watch_table()
stream_rate_table = mongodb_client.get_rate_table()
daily_watch_table = mongodb_client.get_daily_watch_table()

def show_movie_table():
    counter = 0
    for x in movie_table.find():
        print(x)
        counter = counter + 1
        if counter > 10:
            break

def show_user_table():
    counter = 0
    for x in user_table.find():
        print(x)
        counter = counter + 1
        if counter > 10:
            break


def show_watch_table():
    counter = 0
    for x in stream_watch_table.find():
        counter = counter + 1
        if counter < 10:
            print(x)
    print("watch table length: ", counter)


def show_rate_table():
    counter = 0
    for x in stream_rate_table.find():
        counter = counter + 1
        if counter < 10:
            print(x)
    print("rate table length: ", counter)

def get_daily_table():
    result = []
    for x in daily_watch_table.find():
        result.append({"user_id": str(x["user_id"]), "movie_id": str(x["movie_id"]), "query_time": str(x["query_time"])})
    return result


def write_watch_table():
    db = mongodb_client.get_db()
    daily_table = get_daily_table()
    slice = int(len(daily_table) / 7)
    for j in range(1, 8):
        counter = 0
        target_date = datetime.strftime(date.today() - timedelta(j), '%Y-%m-%d')
        table = db["watch_data_" + target_date]
        while counter < slice:
            dict = daily_table[counter + (j-1) * slice]
            print(dict)
            entry = {"user_id": dict["user_id"], "movie_id": dict["movie_id"], "query_time": dict["query_time"]}
            table.insert_one(entry)
            counter = counter + 1

def get_daily_query(table):
    result = []
    for x in table.find():
        if len(x["movies"]) < 100:
            result.append({"user_id": x["user_id"], "movies": x["movies"], "query_time": x["query_time"]})
    return result

def write_query_table():
    db = mongodb_client.get_db()
    today_table = db["2019-10-16_query_table"]
    daily_table = get_daily_query(today_table)
    slice = int(len(daily_table) / 7)
    for j in range(1, 8):
        counter = 0
        target_date = datetime.strftime(date.today() - timedelta(j), '%Y-%m-%d')
        table = db["query_table_" + target_date]
        while counter < slice:
            dict = daily_table[counter + (j - 1) * slice]
            print(dict)
            entry = {"user_id": dict["user_id"], "movies": dict["movies"], "query_time": dict["query_time"]}
            table.insert_one(entry)
            counter = counter + 1

if __name__ == '__main__':
   # print("============== Movie Table ==============")
   # show_movie_table()
   # print("============== User Table ==============")
   # show_user_table()
   # print("============== Watch Table ==============")
   # show_watch_table()
   # print("============== Rate Table ==============")
   # show_rate_table()
   write_watch_table()
   write_query_table()
