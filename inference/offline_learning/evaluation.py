import sys
sys.path.append('../')
from learning_model import Model


if __name__ == "__main__":
    configPath = sys.argv[1]
    m = Model.ModelBasedModel(configPath)
    m.loadModel()
    m.evaluation()