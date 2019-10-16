import unittest
import sys

sys.path.append('../../inference')
from RecommendModule import Model


class TestModel(unittest.TestCase):

    def setUp(self):
        self.MAIN_DIR_PATH = "../../"
        self.WRONG_DIR_PATH = "../"
        self.EXP_NAME = "offl-exp-1"
        self.WRONG_EXP_NAME_SECOND = "offl-exp-a"
        self.WRONG_EXP_NAME = "xpe-1"
        self.model = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.EXP_NAME)

    def test_loadConfig_wrong_expname_case(self):
        with self.assertRaises(AttributeError):
            model1 = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.WRONG_EXP_NAME)
            model1.loadModel()
        with self.assertRaises(AttributeError):
            model2 = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.self.WRONG_EXP_NAME_SECOND)
            model2.loadModel()

    def test_loadConfig_wrong_path_case(self):
        with self.assertRaises(AttributeError):
            model1 = Model.ModelBasedModel(self.WRONG_DIR_PATH, self.EXP_NAME)
            model1.loadModel()

    def test_loadConfig_happy_case(self):
        model1 = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.EXP_NAME)
        model1.loadModel()
        self.assertEqual(model1.config["MODEL_NAME"], "SVD")

if __name__ == '__main__':
    unittest.main()
