"""
This code is used to detect the attack that some users give super high/low scores to a movie compared to its rating in the imdb dataset.

@author Yuchen Wang
"""

"""
This is used to detect whether the last N ratings of a 
particular movie are unusually high or low.
"""

import collections
import requests
import json
import pickle
import time
import numpy as np

class AttackDetector:

    def __init__(self, N):
        super().__init__()
        self.N = N
        self.ENDPOINT = 'http://0.0.0.0:5000/attack_update/'
        self.BATCH_EVERY_SECOND = 5
        self.timer = time.time()
        
        self.movie_to_ratings = collections.defaultdict(list)

        # Since we do not have a database here, I use this dict to illustrate the point.
        self.database = collections.defaultdict(list)
        self.num_rows_database = 0

        self.movie_info = pickle.load(open('feedback_detection_data/movie.info', 'rb'))

    def add_realtime(self, rating_msg):
        l = self.movie_to_ratings[rating_msg['movie']]
        if len(l) == N:
            self.database[rating_msg['movie']].append(l.pop(0))
            self.num_rows_database += 1
        l.append(float(rating_msg['rating']))
    
    def process_realtime(self):
        timestamp = time.time()
        if timestamp - self.timer >= self.BATCH_EVERY_SECOND:
            messages = self.check_movies_attack(self.database, True)
            messages['type'] = 'batch'
            messages['N'] = self.num_rows_database
            requests.post(self.ENDPOINT, json=messages)
            self.timer = timestamp
        messages = self.check_movies_attack(self.movie_to_ratings, False)
        messages['type'] = 'realtime'
        messages['N'] = self.N
        try:
            requests.post(self.ENDPOINT, json=messages)
        except:
            pass

    def check_movies_attack(self, dictionary, is_batch):
        messages = {'messages': [], 'type': 'undefined'}
        for movie_id, ratings in dictionary.items():
            if len(ratings) == self.N:
                # Now compare.
                boolean, msg = self.is_attack(movie_id, is_batch)
                if boolean:
                    messages['messages'].append(msg)
        return messages

    """
    Detect whether a movie is under attack using chebyshev's theorem.
    """
    def is_attack(self, movie_id, is_batch):
        if movie_id not in self.movie_info:
            return False, {}
        imdb_vote = float(self.movie_info[movie_id]['vote_average'])

        # imdb_vote is 0 - 10, but the ratings in our system is 0 - 5
        imdb_vote /= 2

        avg = np.mean(self.movie_to_ratings[movie_id])
        std = np.std(self.movie_to_ratings[movie_id])
        if imdb_vote > avg + 2 * std or imdb_vote < avg - 2 * std:
            return True, {'movie_id': movie_id, 'vote_average': imdb_vote, 'avg_last_N': avg, 'std_last_N': std, 'N': self.num_rows_database if is_batch else self.N}
        return False, {}

    
