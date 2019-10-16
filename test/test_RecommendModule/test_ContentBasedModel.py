import unittest
import sys

sys.path.append('../../inference')
sys.path.append("../../inference/RecommendModule")
from RecommendModule import ContentBaseModel


class TestModel(unittest.TestCase):

    def setUp(self):
        self.MAIN_DIR_PATH = "../../"
        self.REC_NUM = 5
        self.WRONG_REC_NUM = -1
        self.MOVIE_DATA_PATH = "/test/resource/inference/feature/moviefeature.csv"

    def generateModel(self):
        model = ContentBaseModel.ContentModel(self.REC_NUM, self.MAIN_DIR_PATH + self.MOVIE_DATA_PATH)
        return model

    def test_load_moviedata_badcase(self):
        with self.assertRaises(AttributeError):
            ContentBaseModel.ContentModel(self.REC_NUM, self.MOVIE_DATA_PATH)

    def test_contentmodel_training_happycase(self):
        model = self.generateModel()
        self.assertTrue(len(model.topPopularMovieList) > 0)
        self.assertTrue(model.model is not None)
        self.assertTrue(model.modelAppendix is not None)

    def test_recommendation_result(self):
        model = self.generateModel()
        res = model.findSimMovie("46007")
        self.assertTrue(len(res) > 0)
        with self.assertRaises(AttributeError):
            model.findSimMovie("10000")
        res = model.getSimPopularMovie("46007")
        self.assertTrue(len(res) > 0)
        res = model.getSimPopularMovie("10000")
        self.assertTrue(len(res) > 0)


if __name__ == '__main__':
    unittest.main()
