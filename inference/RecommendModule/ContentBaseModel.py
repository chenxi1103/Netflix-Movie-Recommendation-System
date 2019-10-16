import numpy as np
import pyflann
import csv
import random

"""
This is a Content Based Recommendation Model, it recommends similar movie to 
users from users' watch list.
"""


class ContentModel:

    def __init__(self, recNum, MovieDatapath):

        self.trainData = []
        self.movieId2Feature = {}
        self.movieFeatureIndex2MovieId = []
        self.trainDataWithMovieId = []

        self.model = None
        self.modelAppendix = None
        self.recNum = recNum

        self.MovieDatapath = MovieDatapath

        self.loadMovieFeature()
        self.getSimilarity()

        self.topPopularMovieList = []
        self.calculatePopularMovie()

    """
    Train the model 
    """

    def getSimilarity(self):
        flann_kdtree = pyflann.FLANN()
        params_kdtree = flann_kdtree.build_index \
            (np.array(self.trainData, dtype=float), algorithm='kdtree', trees=4)
        self.model = flann_kdtree
        self.modelAppendix = params_kdtree

    def findSimMovie(self, movieId):
        query_feature = np.array(self.movieId2Feature[movieId], dtype=float)
        resultsIndex, dists = self.model.nn_index(query_feature, self.recNum, checks=self.modelAppendix["checks"])
        result = []
        for idx in resultsIndex[0]:
            result.append(self.movieFeatureIndex2MovieId[idx])
        return result

    def calculatePopularMovie(self):
        self.topPopularMovieList = sorted(self.trainDataWithMovieId, key=lambda x:-x[1])[:self.recNum]
        self.topPopularMovieList = [x[0] for x in self.topPopularMovieList]

    def getSimPopularMovie(self, movieId):
        if movieId not in self.movieId2Feature:
            randidx = random.randint(0,self.recNum-1)
            movieId = self.topPopularMovieList[randidx]
        return self.findSimMovie(movieId)


    """
    Rank the merged recommended movie list and rerank the movie list 
    """

    def loadMovieFeature(self):
        with open(self.MovieDatapath, newline='') as csvfile:
            file = csv.reader(csvfile, delimiter=',')
            for row in file:
                fv = []
                for i in range(1, len(row)):
                    fv.append(float(row[i]))
                self.movieId2Feature[row[0]] = fv
                self.trainData.append(fv)
                self.movieFeatureIndex2MovieId.append(row[0])
                self.trainDataWithMovieId.append([row[0]]+fv)


#
# if __name__ == '__main__':
#     c = ContentBasedModel(20, '../feature/moviefeature.csv')
#     print(c.getSimPopularMovie("6305"))
