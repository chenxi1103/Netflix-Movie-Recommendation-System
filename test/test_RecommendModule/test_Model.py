import unittest
import sys
import os
import shutil

sys.path.append('../../inference')
sys.path.append("../../inference/RecommendModule")
from RecommendModule import Model


class TestModel(unittest.TestCase):

    def setUp(self):
        self.MAIN_DIR_PATH = "../../"
        self.WRONG_DIR_PATH = "../"
        self.EXP_NAME = "offl-exp-1"
        self.WRONG_EXP_NAME_SECOND = "offl-exp-a"
        self.WRONG_EXP_NAME = "xpe-1"
        self.model = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.EXP_NAME)
        self.WRONG_CONFIG_FILE_PATH = "test/resource/inference/configuration/wrong_config.json"
        self.TEST_CONFIG_FILE_PATH = "test/resource/inference/configuration/config.json"

    def generate_test_model(self):
        model = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.EXP_NAME)
        model.loadConfig(self.MAIN_DIR_PATH + self.TEST_CONFIG_FILE_PATH, self.EXP_NAME)
        return model

    def test_loadConfig_wrong_expname_case(self):
        with self.assertRaises(AttributeError):
            model1 = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.WRONG_EXP_NAME)
            model1.loadConfig(self.TEST_CONFIG_FILE_PATH, self.WRONG_EXP_NAME)
        with self.assertRaises(AttributeError):
            model2 = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.EXP_NAME)
            model2.loadConfig(self.WRONG_CONFIG_FILE_PATH, self.EXP_NAME)

    def test_loadModel_wrong_path_case(self):
        with self.assertRaises(AttributeError):
            model1 = Model.ModelBasedModel(self.WRONG_DIR_PATH, self.EXP_NAME)
            model1.loadModel()

    def test_loadModel_happy_case(self):
        model1 = self.generate_test_model()
        self.assertEqual(model1.config["MODEL_NAME"], "SVD")

    def test_loadFeature_wrong_case(self):
        self.DATASET_TYPE = "TRAIN"
        model1 = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.EXP_NAME)
        model1.config = model1.loadConfig(self.MAIN_DIR_PATH +self.WRONG_CONFIG_FILE_PATH,
                                          self.EXP_NAME)
        with self.assertRaises(AttributeError):
            model1.loadFeature(self.DATASET_TYPE)

    def test_loadFeature_wrong_dataset_case(self):
        self.DATASET_TYPE = "TRAIN_WRONG"
        model1 = Model.ModelBasedModel(self.MAIN_DIR_PATH, self.EXP_NAME)
        model1.config = model1.loadConfig(self.MAIN_DIR_PATH +self.WRONG_CONFIG_FILE_PATH,
                                          self.EXP_NAME)
        with self.assertRaises(AttributeError):
            model1.loadFeature(self.DATASET_TYPE)

    def test_train_evluate_pipeline_happycase(self):
        model1 = self.generate_test_model()
        model1.train()
        model1.saveModel()
        model1.model = None
        model1.loadModel()
        self.assertTrue(model1 is not None)
        model1.evaluation()
        dirname = model1.MAIN_DIR_PATH + model1.config[model1.MODEL_PATH] + model1.ExpName
        dirlist = os.listdir(model1.MAIN_DIR_PATH + model1.config[model1.MODEL_PATH])
        if len(dirlist) == 1 and dirlist[0] == self.EXP_NAME:
            try:
                shutil.rmtree(dirname)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

    def test_predict_happycase(self):
        model1 = self.generate_test_model()
        model1.train()
        res = model1.predictForEachUser("63184")
        self.assertTrue(len(res) > 0)
        res = model1.predictForEachUser("-1234")
        self.assertTrue(len(res) == 0)

if __name__ == '__main__':
    unittest.main()
