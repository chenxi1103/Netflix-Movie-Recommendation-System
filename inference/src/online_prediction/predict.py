import sys
#TODO change the sys path later
sys.path.append('/Users/yangzhouyi/Desktop/17645/Assignment/HW6G3/17645TeamA/inference')
from learning_model import Model

if __name__ == "__main__":
    configPath, expName = sys.argv[1], sys.argv[2]
    m = Model.ModelBasedModel(configPath, expName)
    m.loadModel()
    print(m.predictForEachUser("12345"))