from utilities import *
import pprint
from time import sleep
import FeedbackLoopUtil
from AttackDetector import AttackDetector


'''
Method to read from the kafka topic
and populate the maps and lists
'''


def read_movielog():
    # Set config vars
    CONFIG_OFFSET = -1
    DEBUG_LIMIT = 100
    # Get the Kafka consumer
    consumer = get_consumer('movielog', CONFIG_OFFSET)

    # Iterate over all messages
    for message in consumer:
        # Parse each message
        message_data = process_message(message.value)

        try:
            # Check if message was invalid
            # Currently, movies without info
            # via API are simply skipped
            if message_data is None:
                continue
            # Update our maps
            try:
                get_and_update_user_info(message_data['user']['user_id'])
                get_and_update_movie_info(message_data['movie']['id'])
            except:
                pass

            # Initialize the user, if it already exists ignore
            init_user_in_map(message_data['user']['user_id'])

            # Handle each type of message separately
            if message_data['type'] == 'DATA':
                data = {}
                data['movie'] = message_data['movie']
                data['timestamp'] = message_data['timestamp']
                user_map[message_data['user']
                         ['user_id']]['watched'].append(data)

            elif message_data['type'] == 'RATING':
                data = {}
                data['movie'] = message_data['movie']
                data['timestamp'] = message_data['timestamp']
                data['rating'] = message_data['rating']
                user_map[message_data['user']
                         ['user_id']]['rated'].append(data)
                data['user_id'] = message_data['user']['user_id']
                rating_list.append(data)
                attack_detector.add_realtime(message_data)

            elif message_data['type'] == 'RR':
                recommendation_list.append(message_data)
                feedback_kafka.realtime_gather_recommendation(message_data)


            # Unknown message, print it out and ignore
            else:
                print(message_data)

        except:
            # Invalid request that could not be parsed
            print('Exception occurred, continuing')
            print(message_data)

        # Print out current status of maps and lists
        print_status()
        feedback_kafka.realtime_process()
        attack_detector.process_realtime()

        # Stop if an arbitary limit has been set
        if DEBUG_LIMIT != -1:
            DEBUG_LIMIT -= - 1
        if DEBUG_LIMIT == 0:
            break

    # Dump all the data via pickle
    # dump_data()

    # Message to exit
    print('That\'s all, folks')


'''
Main method, currently executing the
read_movielog() function
'''



if __name__ == "__main__":
    feedback_kafka = FeedbackLoopUtil.FeedbackLoopUtil('kafka-realtime')
    attack_detector = AttackDetector(20)
    read_movielog()
