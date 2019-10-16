#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-10-12
from kafka import KafkaConsumer
import mongodb_client
import requests

MOVIE_API = 'http://128.2.204.215:8080/movie/'
USER_API = 'http://128.2.204.215:8080/user/'

consumer = KafkaConsumer('movielog', group_id='MovieLog1', bootstrap_servers=['localhost:9092'], api_version=(0, 10))
movie_table = mongodb_client.get_movie_table()
user_table = mongodb_client.get_user_table()
stream_watch_table = mongodb_client.get_watch_table()
stream_rate_table = mongodb_client.get_rate_table()


def query_kafka():
    for msg in consumer:
        parse_msg_value(msg.value)


def kafka_stream_validation(msg):
    data = str(msg).split(',')
    if len(data) == 3:
        return data
    else:
        raise AttributeError("kafka stream data schema is not valid. "
                             "(Does not follow 'Timestamp,user_id,HTTP_query_info' schema")


def write_user_info(user_id):
    if user_id and str(user_id).isdigit():
        query = {"user_id": int(user_id)}
        if user_table.find_one(query) is None:
            api_result = query_user_api(user_id)
            user_table.insert_one(api_result)
        else:
            print("Information of user whose user_id is {0} has already recorded in database.".format(user_id))
    else:
        raise AttributeError("user_id is None or not digits.")


def write_movie_info(movie_id):
    if movie_id is None:
        raise AttributeError("movie_id is None.")
    query = {"id": movie_id}
    # If no info of this movie found, query api and store movie info in db
    if movie_table.find_one(query) is None:
        api_result = query_movie_api(movie_id)
        movie_table.insert_one(api_result)
    else:
        print("Information of movie whose movie_id is {0} has already recorded in database.".format(movie_id))


def write_watch_data(movie_id, query_time, user_id, chunk_num):
    query = {"id": movie_id}
    if movie_table.find_one(query):
        tmdb_id = movie_table.find_one(query)['tmdb_id']
        if tmdb_id and str(tmdb_id).isdigit():
            stream_watch_data = construct_watch_data(query_time, user_id, movie_id, tmdb_id, chunk_num)
            stream_watch_table.insert_one(stream_watch_data)
        else:
            raise AttributeError("tmdb_id for {0} does not exists or not digits.".format(movie_id))


def write_rate_data(movie_id, query_time, user_id, rate):
    query = {"id": movie_id}
    if movie_table.find_one(query):
        tmdb_id = movie_table.find_one(query)['tmdb_id']
        if tmdb_id and str(tmdb_id).isdigit():
            query = {"user_id": user_id, "movie_id": tmdb_id}
            result = stream_rate_table.find_one(query)
            if result is None:
                stream_rate_data = construct_rate_data(query_time, user_id, movie_id, tmdb_id, rate)
                stream_rate_table.insert_one(stream_rate_data)
            # User may rate same movie repeatedly
            else:
                new_value = {"$set": {"query_time": query_time, "score": int(rate)}}
                stream_rate_table.update_one(query, new_value)
                print("User {0} score to movie {1} has updated to {2}".format(user_id, movie_id, rate))
        else:
            raise AttributeError("tmdb_id for {0} does not exists or not digits.".format(movie_id))


def parse_HTTP_request(raw_data):
    data = raw_data.split(" ")
    if len(data) == 2:
        return data
    else:
        raise AttributeError("Invalid HTTP request.")


def parse_detail_request(raw_data):
    data_info = raw_data.split("/")
    if len(data_info) == 3 and data_info[1].strip() == "rate":
        return data_info
    elif len(data_info) == 5 and data_info[1].strip() == "data":
        return data_info
    else:
        raise AttributeError("Invalid request schema. Neither watch data nor rate data.")


def parse_chunk_number(raw_data):
    data = raw_data.split(".")
    if len(data) != 2 or not str(data[0]).isdigit():
        raise AttributeError("Invalid chunk number information.")
    else:
        if int(data[0]) < 0:
            raise AttributeError("Invalid chunk number (should not less than 0).")
        else:
            return int(data[0])


def extract_movie_id_and_rate(raw_data):
    data = raw_data.split("=")
    if len(data) == 2:
        if str(data[1][:-1]).isdigit():
            if int(data[1][:-1]) >= 0 and int(data[1][:-1]) <= 5:
                data[1] = int(data[1][:-1])
                return data
            else:
                raise AttributeError("Movie rate value is not in range of 0 to 5.")
        else:
            raise AttributeError("Movie rate is not a valid integer value.")
    else:
        raise AttributeError("Movie Rate data is in not valid schema.")


def parse_msg_value(msg):
    # First check if incoming kafka stream data schema is valid
    try:
        data = kafka_stream_validation(msg)
        if data[0].startswith("b'"):
            query_time = data[0][2:]
        else:
            query_time = data[0]
        user_id = data[1]
        # If no info of this user found, query api and store user info in db
        write_user_info(user_id)
        http_request = parse_HTTP_request(data[2])
        query_type = http_request[0]
        if query_type == "GET":
            datainfo = parse_detail_request(http_request[1])
            type = datainfo[1]
            if type == "data":
                movie_id = datainfo[3]
                chunk_num = parse_chunk_number(datainfo[4])
                write_movie_info(movie_id)
                write_watch_data(movie_id, query_time, user_id, chunk_num)
            elif type == "rate":
                movie_id = extract_movie_id_and_rate(datainfo[2])[0]
                rate = int(extract_movie_id_and_rate(datainfo[2])[1])
                write_movie_info(movie_id)
                write_rate_data(movie_id, query_time, user_id, rate)
    except AttributeError:
        print("Exception happens.")
        return


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
    try:
        response = requests.get(MOVIE_API + movie_id)
        result = response.json()
        if result["id"] != movie_id:
            raise AttributeError("Movie Not Found From API!")
        else:
            return requests.get(MOVIE_API + movie_id).json()
    except:
        raise AttributeError("API error! Result is not valid JSON format.")


def query_user_api(user_id):
    try:
        response = requests.get(USER_API + user_id)
        result = response.json()
        if str(result["user_id"]) != user_id:
            raise AttributeError("User Not Found From API!")
        else:
            return requests.get(USER_API + user_id).json()
    except:
        raise AttributeError("API error! Result is not valid JSON format.")


if __name__ == '__main__':
    query_kafka()
