import pandas as pd
import time
import os
import sys
import json

import utils.mongodb_client as mongodb_client

rate = mongodb_client.get_rate_table()
THRESHOLD = 0.2

def read_config():
    with open(os.path.join(sys.path[0], 'config.json'), 'r') as f:
        config = json.load(f)
    return config

def extract_user_movie_score():
    count = 0
    total = 0
    d = {'user_id': [], 'movie_id': [], 'score': []}
    rate = mongodb_client.get_rate_table()
    for record in rate.find():
        total += 1
        try:
            user_id, movie_id, score = int(record['user_id']), int(record['movie_id']), int(record['score'])
        except:
            print("Something wrong with a line of MongoDB data.")
            print(record)
            count += 1
        else:
            d['user_id'].append(user_id)
            d['movie_id'].append(movie_id)
            d['score'].append(score)

    if (count > total * THRESHOLD):
        # Do something. Such as sending emails to all developers.
        print("Warning: Possible data schema change or too much missing data")
    return pd.DataFrame.from_dict(d)

def main():
    config = read_config()
    df = extract_user_movie_score()
    df_dedup = df.drop_duplicates(subset=['user_id', 'movie_id', 'score'] ,keep='last')
    file_name = 'user_movie_score_' + str(int(time.time())) + '.csv'
    df_dedup.to_csv(os.path.join(config['model_output_dir'], file_name), index=False)
    copy_file_name = 'usermovie' + '.csv'
    df_dedup.to_csv(os.path.join(config['model_output_dir'], copy_file_name), index=False, header=False)

if __name__ == '__main__':
    main()
