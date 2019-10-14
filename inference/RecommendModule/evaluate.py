import sys
import Model

if __name__ == "__main__":
    mainDirPath, configPath, expName = sys.argv[1], sys.argv[2], sys.argv[3]
    m = Model.ModelBasedModel(mainDirPath, configPath, expName)
    m.loadModel()
    m.evaluation()
