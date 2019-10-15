import unittest
from extract_features import read_config, extract_user_movie_score
import time

import pandas as pd

CONFIG_PARAMS = ['model_output_dir']
MAX_EXTRACT_TIME = 2
MAX_DUPLICATE_RATE = 0.2

class TestExtractFeature(unittest.TestCase):

    def test_read_config(self):
        config = read_config()
        for key in config:
            self.assertTrue(key in CONFIG_PARAMS)

    def test_extract_user_movie_score_size(self):
        df = extract_user_movie_score()
        self.assertTrue(df.shape[1] == 3)

    def test_extract_user_movie_score_time(self):
        start = time.time()
        df = extract_user_movie_score()
        end = time.time()
        self.assertTrue(end - start < MAX_EXTRACT_TIME)

    def test_extract_user_movie_score_dup_rate(self):
        df = extract_user_movie_score()
        total = df.shape[0]
        dup = df.duplicated().sum()
        self.assertTrue(dup / total < MAX_DUPLICATE_RATE)


if __name__ == '__main__':
    unittest.main()