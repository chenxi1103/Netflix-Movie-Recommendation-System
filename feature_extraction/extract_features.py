import pandas as pd
import time
import os
import sys
# import random

import utils.mongodb_client as mongodb_client

rate = mongodb_client.get_rate_table()
THRESHOLD = 0.2

def extract_user_movie_score():
    count = 0
    total = 0
    d = {'user_id': [], 'movie_id': [], 'score': []}
    rate = mongodb_client.get_rate_table()
    for record in rate.find():
        total += 1
        try:
            user_id, movie_id, score = int(record['user_id']), int(record['movie_id']), int(record['score'])
            # if (random.random() > 0.4):
            #     raise ValueError
        except:
            print("Something wrong with a line of MongoDB data.")
            count += 1
        else:
            d['user_id'].append(user_id)
            d['movie_id'].append(movie_id)
            d['score'].append(score)

    if (count > total * THRESHOLD):
        # Do something. Such as sending emails to all developers.
        print("Warning: Possible data schema change or too much missing data")
    df = pd.DataFrame.from_dict(d).drop_duplicates(keep='last')
    
    file_name = 'user_movie_score_' + str(int(time.time())) + '.csv'
    df.to_csv(os.path.join(sys.path[0], 'data', file_name))

if __name__ == '__main__':
    extract_user_movie_score()