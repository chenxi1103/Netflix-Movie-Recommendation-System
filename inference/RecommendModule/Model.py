from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate

from surprise import KNNBasic
from surprise import KNNWithMeans
from surprise import KNNWithZScore
from surprise import SVD
from surprise import SVDpp
from surprise import NMF
from surprise import SlopeOne
from surprise import CoClustering

from collections import defaultdict
import os
import json
import pickle

"""
This class uses model-base model (SVD, MF ..) to recommend movies
"""


class ModelBasedModel:

    def __init__(self, MainDirPath, ConfigPath, ExpName):
        self.MODEL_NAME = "MODEL_NAME"
        self.FEATURE_PATH = "FEATURE_PATH"
        self.TEST_FEATURE_PATH = "TEST_FEATURE_PATH"
        self.MODEL_DICT = {"KNNBasic": KNNBasic(), "KNNWithMeans": KNNWithMeans(),
                           "KNNWithZScore": KNNWithZScore(), "SVD": SVD(),
                           "SVDpp": SVDpp(), "NMF": NMF(),
                           "SlopeOne": SlopeOne(), "CoClustering": CoClustering()}
        self.TOP_RECOMMEND_RESULT_NUM = "TOP_RECOMMEND_RESULT_NUM"
        self.MODEL_PATH = "MODEL_PATH"
        self.HYPER_PARAMETER = "HYPER_PARAMETER"
        self.MAIN_DIR_PATH = MainDirPath
        self.ExpName = ExpName
        self.trainset, self.testset = None, None
        self.config = self.loadConfig(os.path.expanduser(ConfigPath), ExpName)
        self.model = self.MODEL_DICT[self.config[self.MODEL_NAME]]

    def loadConfig(self, filePath, ExpName):
        d = {}
        with open(filePath) as fp:
            d = json.load(fp)
        if ExpName not in d:
            raise AttributeError
        config = d[ExpName]
        return config

    def loadFeature(self, dataset_type):
        reader = Reader(line_format='user item rating', sep=',')
        if dataset_type == "TRAIN":
            filePath = self.MAIN_DIR_PATH + self.config[self.FEATURE_PATH]
            data = Dataset.load_from_file(filePath, reader=reader)
            self.trainset = data.build_full_trainset()
        elif dataset_type == "EVALUATION":
            filePath = self.MAIN_DIR_PATH + self.config[self.TEST_FEATURE_PATH]
            data = Dataset.load_from_file(filePath, reader=reader)
            self.testset = data.build_full_trainset()
        else:
            raise AttributeError

    def saveModel(self):
        dirname = self.MAIN_DIR_PATH + self.config[self.MODEL_PATH] + self.ExpName
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        filePath = dirname + '/model.pkl'
        with open(filePath, 'wb') as fp:
            pickle.dump(self.model, fp)

    def loadModel(self):
        dirname = self.MAIN_DIR_PATH + self.config[self.MODEL_PATH] + self.ExpName
        filePath = dirname + '/model.pkl'
        with open(filePath, 'rb') as fp:
            self.model = pickle.load(fp)

    def predictForEachUser(self, userId):
        self.loadFeature("TRAIN")
        pred = self.model.test(self.trainset.build_testset())
        topn = self.get_top_n(pred, self.config[self.TOP_RECOMMEND_RESULT_NUM])
        return topn[userId]

    def train(self):
        self.loadFeature("TRAIN")
        self.model.fit(self.trainset)

    def evaluation(self):
        self.loadFeature("EVALUATION")
        predictions = self.model.test(self.testset.build_testset())
        evaluation_k, evaluation_threshold = 5, 4
        precisions, recalls = self.precision_recall_at_k(predictions, k=evaluation_k, threshold=evaluation_threshold)
        # Precision and recall can then be averaged over all users
        precision = sum(prec for prec in precisions.values()) / len(precisions)
        recall = sum(rec for rec in recalls.values()) / len(recalls)
        print(precision, recall)
        dirname = self.config[self.MODEL_PATH] + self.ExpName
        filePath = self.MAIN_DIR_PATH+ dirname + '/evaluation_result.txt'
        with open(filePath, 'w') as fp:
            fp.write("ModelType: %s \n" % self.config[self.MODEL_NAME])
            fp.write("HyperParameter: %s\n" % json.dumps(self.config[self.HYPER_PARAMETER]))
            fp.write("evaluation_k: %d\n" % evaluation_k)
            fp.write("evaluation_threshold: %d\n" % evaluation_threshold)
            fp.write("Precision: %f \n" % precision)
            fp.write("Recall: %f \n" % recall)

    '''
    Return the top-N recommendation for each user from a set of predictions.
    Args:
        predictions(list of Prediction objects): The list of predictions, as
                returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
                is 10.
    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
            [(raw item id, rating estimation), ...] of size n.
    '''

    def get_top_n(self, predictions, n=10):

        # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))

        # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n

    """
    This function predicts the RMSE of predicted movie rating
    """

    def EvaluateRMSEwithCrossValidation(self):
        algo = self.model
        cross_validate(algo, self.trainset, measures=['RMSE', 'MAE'], cv=5, verbose=True)

    """
    This function predicts the RMSE of predicted movie rating
    """

    def EvaluatePrecisionRecallwithRating(self):
        algo = self.model
        algo.fit(self.trainset)
        print(dir(algo))
        predictions = algo.test(self.testset)
        # for pred in predictions:
        #    print("prediction:", pred)
        topn = self.get_top_n(predictions)
        precisions, recalls = self.precision_recall_at_k(predictions, k=5, threshold=3)
        # Precision and recall can then be averaged over all users
        print(sum(prec for prec in precisions.values()) / len(precisions))
        print(sum(rec for rec in recalls.values()) / len(recalls))

    def EvaluatePrecisionRecallwithHitNum(self):
        algo = self.model
        algo.fit(self.trainset)
        predictions = algo.test(self.testset)
        precisions, recalls = self.precision_recall_by_hit_num(predictions, self.testset)
        # Precision and recall can then be averaged over all users
        print(sum(prec for prec in precisions.values()) / len(precisions))
        print(sum(rec for rec in recalls.values()) / len(recalls))

    """
    This function calculates the precision and recall
    It considers the recommended movie that has an actual rating that is higher than a threshold as relevent
    This function is from official suprise website https://surprise.readthedocs.io/en/stable/FAQ.html
    """

    def precision_recall_at_k(self, predictions, k, threshold):
        '''Return precision and recall at k metrics for each user.'''

        # First map the predictions to each user.
        user_est_true = defaultdict(list)
        for uid, _, true_r, est, _ in predictions:
            user_est_true[uid].append((est, true_r))
        precisions = dict()
        recalls = dict()
        for uid, user_ratings in user_est_true.items():
            # Sort user ratings by estimated value
            user_ratings.sort(key=lambda x: x[0], reverse=True)
            # Number of relevant items
            n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
            # Number of recommended items in top k
            n_rec_k = sum((est >= threshold) for (est, _) in user_ratings[:k])
            # Number of relevant and recommended items in top k
            n_rel_and_rec_k = sum(((true_r >= threshold) and (est >= threshold))
                                  for (est, true_r) in user_ratings[:k])
            # Precision@K: Proportion of recommended items that are relevant
            precisions[uid] = n_rel_and_rec_k / n_rec_k if n_rec_k != 0 else 1
            # Recall@K: Proportion of relevant items that are recommended
            recalls[uid] = n_rel_and_rec_k / n_rel if n_rel != 0 else 1

        return precisions, recalls

    """
    This function calculates the precision and recall
    It considers the recommended movie that is in the user's watchlist as relevant
    This function is from official suprise website https://surprise.readthedocs.io/en/stable/FAQ.html
    """

    def precision_recall_by_hit_num(self, predictions, testset):
        # Todo Edit Later
        # First map the predictions to each user.
        user_est_true = defaultdict(list)
        for uid, movieId, true_r, est, _ in predictions:
            user_est_true[uid].append((est, true_r, movieId))

        precisions = dict()
        recalls = dict()
        user2TestMovieID = defaultdict(dict)
        user2RecMovieId = defaultdict(dict)

        for (userId, movieId, rate) in testset:
            user2TestMovieID[userId][movieId] = rate

        for uid, movieId, true_r, est, _ in predictions:
            user2RecMovieId[uid][movieId] = est

        hitNum = 0
        relevantMovieNum = 0
        recommenMovieNum = 0
        for uid in user2TestMovieID:
            testMovieList = user2TestMovieID[uid]
            recMovieList = user2RecMovieId[uid]
            relevantMovieNum += len(testMovieList)
            recommenMovieNum += len(recMovieList)
            hitNum = len(set(testMovieList).intersection(set(recMovieList)))

        precisions[0] = hitNum / (1.0 * recommenMovieNum)
        recalls[0] = hitNum / (1.0 * relevantMovieNum)

        return precisions, recalls


if __name__ == '__main__':
    pass
