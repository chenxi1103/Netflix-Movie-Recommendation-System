import sys
from flask import Flask
sys.path.append('/home/teama/17645TeamA/inference')
from RecommendModule import Model
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/recommend/<user_id>')
def inference(user_id):
    dic[userid] +=1
    return str(m.predictForEachUser(str(user_id)))

if __name__ == "__main__":
    mainDirPath, configPath, expName = sys.argv[1], sys.argv[2], sys.argv[3]
    m = Model.ModelBasedModel(mainDirPath, configPath, expName)
    m.loadModel()
    app.run(host='0.0.0.0', port=8082)
