import time
import json
import requests
import collections
import pickle
import os
import numpy as np
import threading

class FeedbackLoopUtil:
    def __init__(self, mode):
        self.mode = mode
        self.MONITOR_SERVICE_URL = 'http://0.0.0.0:5000/feedback_update/'
        # movie to genre dict: key:movie_id, value: genre list
        self.movie_genre_dict = pickle.load(open('feedback_detection_data/movie_genre_dict.pkl', 'rb'))
        self.genre_cnt_dict = pickle.load(open('feedback_detection_data/genre_total_cnt.pkl', 'rb'))
        self.log_path = './history_recommend/'
        self.batch_process_res_path = 'feedback_detection_data/batch_result.pkl'
        self.HISTORY_LOG_NUM = 5  # calculate 5 * LONG_TIME_INTERVAL range avg movie genre ratio
        now_time = time.time()

        if mode == 'kafka-realtime':
            self.global_start_time = now_time
            self.incremental_start_time = int(round(1000 * now_time))
            self.incremental_long_start_time = int(now_time)
            self.today = time.localtime(now_time).tm_mday
            self.incremental_recommend_dict = collections.defaultdict(dict)
            self.accumulate_recommend_dict = collections.defaultdict(dict)
            self.SHORT_TIME_INTERVAL = 1000  # ms
            self.LONG_TIME_INTERVAL = 3600  # second

        elif mode == 'batch-process':
            self.BATCH_PROCESS_INTERVAL = 7200
            t = threading.Timer(self.BATCH_PROCESS_INTERVAL, self.batch_process)
            t.start()

        elif mode == 'monitor-service':
            self.backup_msg = "backup_msg"
            self.latest_avg_movie_genre_ratio = pickle.load(open(self.batch_process_res_path, 'rb'))
            self.realtime_movie_genre = collections.defaultdict(collections.Counter)
        else:
            raise AttributeError('Do not support such mode')

    '''
        Collect recommend data genre info 
    '''

    def realtime_gather_recommendation(self, recomend_msg):
        team = recomend_msg['team']
        recommened_movie_list = recomend_msg['recommendations']
        for movie_id in recommened_movie_list:
            for genre in self.movie_genre_dict[movie_id]:
                self.incremental_recommend_dict[team].setdefault(genre, 0)
                self.incremental_recommend_dict[team][genre] += 1
                self.accumulate_recommend_dict[team].setdefault(genre, 0)
                self.accumulate_recommend_dict[team][genre] += 1

    '''
        Feedback Loop real time process part
        Calculate time and send recommend data to monitor service (or dump data) on time
    '''

    def realtime_process(self):
        now_time = time.time()
        # send real time data per minute
        if int(round(1000 * now_time)) - self.incremental_start_time > self.SHORT_TIME_INTERVAL:
            self.incremental_start_time = int(round(1000 * now_time))
            msg = {}
            for team in self.incremental_recommend_dict:
                msg[team] = {'data': self.incremental_recommend_dict[team]}
            if msg:
                msg['type'] = 'kafka-realtime'
                msg = json.dumps(msg)
                try:
                    requests.post(self.MONITOR_SERVICE_URL, json=msg)
                except:
                    pass
                self.incremental_recommend_dict = collections.defaultdict(dict)

        # dump accumlated data per day
        if int(now_time) - self.incremental_long_start_time > self.LONG_TIME_INTERVAL:
            if not os.path.exists(self.log_path):
                os.mkdir(self.log_path)
            file_name = str(int(now_time)) + '.pkl'
            pickle.dump(self.accumulate_recommend_dict, open(os.path.join(self.log_path, file_name), 'wb'))
            self.accumulate_recommend_dict = collections.defaultdict(dict)
            self.incremental_long_start_time = int(now_time)
            # self.batch_process()

    '''
        Feedback Loop batch process part
    '''

    def batch_process(self):
        movie_ratio_dict_list = self.load_latest_movie_ratio()
        res = collections.defaultdict(dict)
        total_cnt = 0
        for epoch, _ in enumerate(movie_ratio_dict_list):
            for team in movie_ratio_dict_list[epoch]:
                total_cnt += sum(movie_ratio_dict_list[epoch][team][key] for key in movie_ratio_dict_list[epoch][team])
                for movie_genre in self.genre_cnt_dict:
                    # using laplace smoothing
                    if movie_genre in movie_ratio_dict_list[epoch][team]:
                        res[team][movie_genre] = (1 + movie_ratio_dict_list[epoch][team][movie_genre]) / (
                                len(self.genre_cnt_dict) + total_cnt)
                    else:
                        res[team][movie_genre] = 1 / len(self.genre_cnt_dict)
        print('batch_process_res')
        pickle.dump(res, open(self.batch_process_res_path, 'wb'))
        msg = {}
        msg['type'] = 'batch-process'
        msg = json.dumps(msg)
        try:
            requests.post(self.MONITOR_SERVICE_URL, json=msg)
        except:
            pass

        t = threading.Timer(self.BATCH_PROCESS_INTERVAL, self.batch_process)
        t.start()
        return res

    '''
        Feedback Loop detection in monitor service part
    '''

    def monitor_process(self, msg):
        msg = json.loads(msg)
        if msg['type'] == 'kafka-realtime':
            for key in msg:
                if key != 'type':
                    self.realtime_movie_genre[key] = collections.Counter(msg[key]['data'])
            real_time_movie_ratio = self.calculate_ratio()
            different_score_res = self.calcualte_L2_difference(real_time_movie_ratio)
            res = self.generate_monitor_result(different_score_res, real_time_movie_ratio)
            self.backup_msg = json.dumps(res)
            return self.backup_msg
        elif msg['type'] == 'batch-process':
            if os.path.getsize(self.batch_process_res_path) > 0:
                self.latest_avg_movie_genre_ratio = pickle.load(open(self.batch_process_res_path, 'rb'))
            return self.backup_msg
        else:
            raise AttributeError

    '''
        Calculate movie genre ratio according to the movie's genre count
    '''

    def calculate_ratio(self):
        res = collections.defaultdict(dict)
        for team in self.realtime_movie_genre:
            total_cnt = sum(self.realtime_movie_genre[team][key] for key in self.realtime_movie_genre[team])
            for movie_genre in self.genre_cnt_dict:
                # using laplace smoothing
                if movie_genre in self.realtime_movie_genre[team]:
                    res[team][movie_genre] = (1 + self.realtime_movie_genre[team][movie_genre]) / (
                            len(self.genre_cnt_dict) + total_cnt)
                else:
                    res[team][movie_genre] = 1 / len(self.genre_cnt_dict)
        return res

    '''
        Using KL divergence to calculate the difference between real-time movie genre ratio and 
        history movie genre ratio
    '''

    def calcualte_KL_difference(self, real_time_movie_ratio):
        res = {}
        for team in real_time_movie_ratio:
            tmp_res = 0
            for movie_genre in self.genre_cnt_dict:
                p = self.latest_avg_movie_genre_ratio[team][movie_genre]
                q = real_time_movie_ratio[team][movie_genre]
                tmp_res += p * np.log(p / q)
            res[team] = tmp_res
        return res

    '''
        Using Cosine similarity to calculate the difference between real-time movie genre ratio and 
        history movie genre ratio
    '''

    def calcualte_L2_difference(self, real_time_movie_ratio):
        res = {}
        for team in real_time_movie_ratio:
            tmp_res = 0
            for movie_genre in self.genre_cnt_dict:
                p = self.latest_avg_movie_genre_ratio[team][movie_genre]
                q = real_time_movie_ratio[team][movie_genre]
                tmp_res += (p - q) ** 2
            res[team] = np.sqrt(tmp_res / len(self.genre_cnt_dict))
        return res

    '''
        generate monitor result for front end display
    '''

    def generate_monitor_result(self, difference_score, real_time_movie_ratio):
        res = {}
        for team in real_time_movie_ratio:
            if team in difference_score:
                res[team] = {'ratio': real_time_movie_ratio[team], 'difference_score': difference_score[team]}
            else:
                res[team] = {'ratio': real_time_movie_ratio[team], 'difference_score': 0.0}
        return res

    '''
        load latest aggregated movie ratio result
    '''

    def load_latest_movie_ratio(self):
        file_list = os.listdir(self.log_path)
        if len(file_list) <= self.HISTORY_LOG_NUM:
            sorted_file_list = file_list
        else:
            sorted_file_list = sorted(file_list, reverse=True)[:self.HISTORY_LOG_NUM]
        movie_ratio_dict_list = []
        for file in sorted_file_list:
            movie_ratio_dict_list.append(pickle.load(open(os.path.join(self.log_path, file), 'rb')))
        return movie_ratio_dict_list
