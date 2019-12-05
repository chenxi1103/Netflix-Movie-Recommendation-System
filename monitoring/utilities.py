from kafka import KafkaConsumer
from kafka import TopicPartition
import json
import requests
import sys
import pickle

import urllib.parse
import dateutil.parser

# Config vars
KAFKA_TIMEOUT = 10000
URL_MOVIE_API = 'http://128.2.204.215:8080/movie/'
URL_USER_API = 'http://128.2.204.215:8080/user/'

# Maps and lists
user_map = {}
user_info = {}
movie_info = {}
rating_list = []
recommendation_list = []

'''
Method to return a Kafka consumer, with an optional offset
'''


def get_consumer(topic, offset=-1):
    # Check for offset, otherwise return consumer with group_id
    if offset == -1:
        consumer = KafkaConsumer(
            topic, group_id='MovieLog1', consumer_timeout_ms=KAFKA_TIMEOUT)
    else:
        consumer = KafkaConsumer(consumer_timeout_ms=KAFKA_TIMEOUT)
        consumer.assign([TopicPartition(topic, offset)])
        consumer.seek_to_beginning(TopicPartition(topic, offset))
    return consumer


'''
Method to get a movie's info from the API, and update
the internal map
'''


def get_and_update_movie_info(raw_code):
    try:
        # Try to return from the internal map
        if raw_code in movie_info:
            return movie_info[raw_code]
        # Check if the API returns the relevant data
        temp = requests.get(
            URL_MOVIE_API + raw_code).json()
        # Detect if the response does not have the data
        if 'message' in temp:
            return None
        # Add the movie to the map
        movie_info[raw_code] = temp
        # Return the movie data
        return movie_info[raw_code]
    except:
        # If an error occurs, return None
        return None


'''
Method to get a user's info from the API, and update
the internal map
'''


def get_and_update_user_info(user_id):
    try:
        # Try to return from the internal map
        if user_id in user_info:
            return user_info[user_id]
        # Check if the API returns the relevant data
        temp = requests.get(URL_USER_API + user_id).json()
        if 'message' in temp:
            return None
        # Add the user to the map
        user_info[user_id] = temp
        # Return the user data
        return user_info[user_id]
    except:
        # If an error occurs, return None
        return None


'''
Method to parse the raw message from the Kafka stream,
decode, process and derive useful information and return
a constructed JSON object containing the useful info
'''


def process_message(msg_str):
    # Try to handle malformed messages
    try:
        # Decode the message
        msg_str = str(msg_str.decode('utf-8')).lower()
        # Split on the fields
        msg_split = msg_str.split(',')
        # Construct the dict
        msg_data = {}

        # Parse message based on its types:
        # Set the type, and subsequently add the relevant fields
        if 'get /data' in msg_str:
            msg_data['type'] = 'DATA'
            msg_data['timestamp'] = msg_split[0].strip()
            user_info = get_and_update_user_info(msg_split[1].strip())
            if user_info is None:
                return None
            msg_data['user'] = user_info
            movie_info = get_and_update_movie_info(
                msg_split[2].split('/')[3].strip())
            if movie_info is None:
                return None
            msg_data['movie'] = movie_info
            msg_data['movie_part'] = msg_split[2].split(
                '/')[4].strip().split('.')[0]

        elif 'get /rate' in msg_str:
            msg_data['type'] = 'RATING'
            msg_data['timestamp'] = msg_split[0].strip()
            user_info = get_and_update_user_info(msg_split[1].strip())
            if user_info is None:
                return None
            msg_data['user'] = user_info
            movie_info = get_and_update_movie_info(
                msg_split[2].split('/')[2].split('=')[0].strip())
            if movie_info is None:
                return None
            msg_data['movie'] = movie_info
            msg_data['rating'] = int(urllib.parse.unquote_plus(
                msg_split[2].split('/')[2].split('=')[1].strip()))

        elif 'recommendation request' in msg_str:
            msg_data['status'] = msg_split[3].strip().split(' ')[1].strip()
            if msg_data['status'] != '200':
                return None
            msg_data['team'] = msg_split[2].split(
                ' ')[2].split('.')[0].split('-')[1]
            msg_data['type'] = 'RR'
            msg_data['timestamp'] = msg_split[0].strip()
            msg_data['user'] = {}
            msg_data['user']['user_id'] = msg_split[1].strip()

            res = msg_split[4:]
            new_res = []
            for r in res:
                r = r.replace('result: ', '')
                r = r.strip()
                # r = urllib.parse.unquote_plus(r.strip())
                new_res.append(r)

            msg_data['recommendations'] = new_res

        # Placeholder for unidentified messages
        else:

            print('Unable to classify message:')
            print(msg_str)
            # Skip it from the consumer
            msg_data = None
    except:
        # Return None for a message that
        # does not obey expected format
        msg_data = None

    # Return the parsed message
    return msg_data


'''
Method to initialize the user in
the map, if not present already
'''


def init_user_in_map(id):
    if not id in user_map:
        user_map[id] = {}
        user_map[id]['watched'] = []
        user_map[id]['rated'] = []


'''
Method to print the current status
of the internal maps and lists
'''


def print_status():
    print('Records: user data: ' + str(len(user_map)) + ' | user info: ' +
          str(len(user_info)) + ' | movie info: ' + str(len(movie_info)) +
          ' | rating list: ' + str(len(rating_list)) + ' | recommendation list: ' +
          str(len(recommendation_list)))


'''
Method to dump the data from the
internal maps and lists
'''


def dump_data():
    with open('user.map', 'wb') as f:
        pickle.dump(user_map, f)
    with open('user.info', 'wb') as f:
        pickle.dump(user_info, f)
    with open('movie.info', 'wb') as f:
        pickle.dump(movie_info, f)
    with open('rating.list', 'wb') as f:
        pickle.dump(rating_list, f)
    with open('recommendation.list', 'wb') as f:
        pickle.dump(recommendation_list, f)
