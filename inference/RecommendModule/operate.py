import sys
import Model

if __name__ == "__main__":
    mainDir, expName = sys.argv[1], sys.argv[2]

    for arg in sys.argv[3:]:
        if arg not in ["Train", "Evaluation","Predict"]:
            raise(AttributeError("argment error"))
    m = Model.ModelBasedModel(mainDir, expName)
    if "Train" in sys.argv:
        m.train()
        m.saveModel()
        sys.exit(0)
    if "Evaluation" in sys.argv:
        m.loadModel()
        evaluation_pass = m.evaluation()
        if not evaluation_pass:
            print("Evaluation Failed")
            sys.exit(1)
        sys.exit(0)
    if "Predict" in sys.argv:
        m.loadModel()
        print(m.predictForEachUser("63186"))
        sys.exit(0)
