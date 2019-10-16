import sys
import Model

if __name__ == "__main__":
    mainDir, expName = sys.argv[1], sys.argv[2]
    m = Model.ModelBasedModel(mainDir, expName)
    if "Train" in sys.argv:
        m.train()
        m.saveModel()
    if "Evaluation" in sys.argv:
        m.loadModel()
        m.evaluation()
    if "Predict" in sys.argv:
        m.loadModel()
        print(m.predictForEachUser("12345"))
