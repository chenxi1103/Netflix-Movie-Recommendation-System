#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-10-12
from kafka import KafkaConsumer
import mongodb_client
import requests

MOVIE_API = 'http://128.2.204.215:8080/movie/'
USER_API = 'http://128.2.204.215:8080/user/'

consumer = KafkaConsumer('movielog', group_id='MovieLog1', bootstrap_servers= ['localhost:9092'], api_version = (0, 10))
movie_table = mongodb_client.get_movie_table()
user_table = mongodb_client.get_user_table()
stream_watch_table = mongodb_client.get_watch_table()
stream_rate_table = mongodb_client.get_rate_table()

def query_kafka():
    for msg in consumer:
        parse_msg_value(msg.value)

def parse_msg_value(msg):
    data = str(msg).split(',')
    query_time = data[0]
    user_id = data[1]
    # If no info of this user found, query api and store user info in db
    if user_id:
        query = {"user_id": user_id}
        if user_table.find_one(query) is None:
            api_result = query_user_api(user_id)
            user_table.insert_one(api_result)

    query_type = data[2].split(" ")[0]
    if query_type == "GET":
        info = data[2].split(" ")[1]
        datainfo = info.split("/")
        type = datainfo[1]
        # Watch data
        if type == 'data':
            movie_id = datainfo[3]
            chunk_num = int(datainfo[4].split(".")[0])
            if movie_id:
                query = {"id": movie_id}
                # If no info of this movie found, query api and store movie info in db
                if movie_table.find_one(query) is None:
                    api_result = query_movie_api(movie_id)
                    movie_table.insert_one(api_result)
                if movie_table.find_one(query):
                    tmdb_id = movie_table.find_one(query)['tmdb_id']
                    stream_watch_data = construct_watch_data(query_time, user_id, movie_id, tmdb_id, chunk_num)
                    stream_watch_table.insert_one(stream_watch_data)
        # Rate data
        elif type == 'rate':
            movie_id= datainfo[2].split("=")[0]
            rate = int(datainfo[2].split("=")[1][:-1])
            if movie_id:
                query = {"id": movie_id}
                # If no info of this movie found, query api and store movie info in db
                if movie_table.find_one(query) is None:
                    api_result = query_movie_api(movie_id)
                    movie_table.insert_one(api_result)
                if movie_table.find_one(query):
                    tmdb_id = movie_table.find_one(query)['tmdb_id']
                    stream_rate_data = construct_rate_data(query_time, user_id, movie_id, tmdb_id, rate)
                    stream_rate_table.insert_one(stream_rate_data)

def construct_watch_data(query_time, user_id, movie_name, movie_id, chunk_num):
    data = {}
    data["query_time"] = query_time
    data["user_id"] = user_id
    data["movie_id"] = movie_id
    data["movie_name"] = movie_name
    data["chunk_num"] = chunk_num
    return data

def construct_rate_data(query_time, user_id, movie_name, movie_id, score):
    data = {}
    data["query_time"] = query_time
    data["user_id"] = user_id
    data["movie_id"] = movie_id
    data["movie_name"] = movie_name
    data["score"] = score
    return data

def query_movie_api(movie_id):
    return requests.get(MOVIE_API + movie_id).json()

def query_user_api(user_id):
    return requests.get(USER_API + user_id).json()

if __name__ == '__main__':
    query_kafka()
