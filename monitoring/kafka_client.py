#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-11-24
from kafka import KafkaConsumer
import mongodb_client

rate_table = mongodb_client.get_rate_table()
consumer = KafkaConsumer('movielog', group_id='MovieLog1', bootstrap_servers=['localhost:9092'], api_version=(0, 10))

def parse_rate():
    for msg in consumer:
        flag, query_time, user_id, movie_name, score = get_rate_info(str(msg.value, encoding="utf-8"))
        if flag:
            stream_rate_data = construct_rate_data(query_time, user_id, movie_name, score)
            rate_table.insert_one(stream_rate_data)
            print(stream_rate_data)

def construct_rate_data(query_time, user_id, movie_name, score):
    data = {}
    data["query_time"] = query_time
    data["user_id"] = user_id
    data["movie_name"] = movie_name
    data["score"] = score
    return data

def get_rate_info(msg):
    if len(msg.split(",")) >= 3:
        data = msg.split(",")[2]
        if len(data.split(" ")) == 2 and data.split(" ")[1].split("/")[1] == 'rate':
            user_id = msg.split(",")[1]
            query_time = msg.split(",")[0]
            movie_name = data.split(" ")[1].split("/")[2].split("=")[0]
            score = data.split(" ")[1].split("/")[2].split("=")[1]
            return True, query_time, user_id, movie_name, score
        else:
            return False, None, None, None, None
    return False, None, None, None, None



if __name__ == '__main__':
    parse_rate()