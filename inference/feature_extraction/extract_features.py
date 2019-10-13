import pandas as pd
import time
import os
import sys

import utils.mongodb_client as mongodb_client

rate = mongodb_client.get_rate_table()

def extract_user_movie_score():
    d = {'user_id': [], 'movie_id': [], 'score': []}
    rate = mongodb_client.get_rate_table()
    for record in rate.find():
        d['user_id'].append(int(record['user_id']))
        d['movie_id'].append(int(record['movie_id']))
        d['score'].append(int(record['score']))
    df = pd.DataFrame.from_dict(d)
    
    file_name = 'user_movie_score_' + str(int(time.time())) + '.csv'
    df.to_csv(os.path.join(sys.path[0], 'data', file_name))

if __name__ == '__main__':
    extract_user_movie_score()