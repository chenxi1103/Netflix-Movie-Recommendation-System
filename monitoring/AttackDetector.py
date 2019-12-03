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
import numpy as np

class AttackDetector:

    def __init__(self, N):
        super().__init__()
        self.N = N
        self.ENDPOINT = 'http://0.0.0.0:5000/attack_update/'
        
        self.movie_to_ratings = collections.defaultdict(list)
        self.movie_info = pickle.load(open('feedback_detection_data/movie.info', 'rb'))

    def add_realtime(self, rating_msg):
        l = self.movie_to_ratings[rating_msg['movie']]
        if len(l) == N:
            l.pop(0)
        l.append(float(rating_msg['rating']))
    
    def process_realtime(self):
        messages = []
        for movie_id, ratings in self.movie_to_ratings.items():
            if len(ratings) == self.N:
                # Now compare.
                boolean, msg = self.is_attack(movie_id)
                if boolean:
                    messages.append(msg)
        requests.post(self.ENDPOINT, json=messages)

    """
    Detect whether a movie is under attack using chebyshev's theorem.
    """
    def is_attack(self, movie_id):
        if movie_id not in self.movie_info:
            return False, {}
        imdb_vote = float(self.movie_info[movie_id]['vote_average'])

        # imdb_vote is 0 - 10, but the ratings in our system is 0 - 5
        imdb_vote /= 2

        avg = np.mean(self.movie_to_ratings[movie_id])
        std = np.std(self.movie_to_ratings[movie_id])
        if imdb_vote > avg + 2 * std or imdb_vote < avg - 2 * std:
            return True, {'movie_id': movie_id, 'vote_average': imdb_vote, 'avg_last_N': avg, 'std_last_N': std, 'N': self.N}
        return False, {}

    
