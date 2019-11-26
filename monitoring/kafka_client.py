#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-11-24
from kafka import KafkaConsumer
import json
import mongodb_client

rate_table = mongodb_client.get_rate_table()
beta_table = mongodb_client.get_beta_table()
alpha_table = mongodb_client.get_alpha_table()
charlie_table = mongodb_client.get_charlie_table()


consumer = KafkaConsumer('movielog', group_id='MovieLog1', bootstrap_servers=['localhost:9092'], api_version=(0, 10))

def parse():
    for msg in consumer:
        infos = str(msg.value, encoding="utf-8")
        flag, query_time, user_id, movie_name, score = get_rate_info(infos)
        if flag:
            stream_rate_data = construct_rate_data(query_time, user_id, movie_name, score)
            rate_table.insert_one(stream_rate_data)
            # print(stream_rate_data)
        else:
            info = infos.split(",")[2].split(" ")
            if info[0] != "GET":
                if len(info) >= 3 and info[2] == "17656-Beta.isri.cmu.edu:8082":
                    json_data = construct_recommend(infos)
                    if json_data is not None:
                        beta_table.insert_one(json_data)
                elif len(info) >= 3 and info[2] == "17656-Alpha.isri.cmu.edu:8082":
                    json_data = construct_recommend(infos)
                    if json_data is not None:
                        alpha_table.insert_one(json_data)
                elif len(info) >= 3 and info[2] == "17656-Charlie.isri.cmu.edu:8082":
                    json_data = construct_recommend(infos)
                    if json_data is not None:
                        charlie_table.insert_one(json_data)

def construct_rate_data(query_time, user_id, movie_name, score):
    data = {}
    data["query_time"] = query_time
    data["user_id"] = user_id
    data["movie_name"] = movie_name
    data["score"] = score
    return data

def construct_recommend_json(user_id, recommend_result, timestamp):
    data = {}
    data["timestamp"] = timestamp
    data["user_id"] = user_id
    data["result"] = recommend_result
    return data

def construct_recommend(msg_value):
    data = msg_value.split(",")
    if data[3].strip().split(" ")[1] == '200':
        user_id = data[1]
        recommend_result = msg_value.split(" result: ")[1].split(", ")[:-1]
        time_stamp = data[0]
        json_data = construct_recommend_json(user_id, recommend_result, time_stamp)
        return json_data
    return None

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
    parse()