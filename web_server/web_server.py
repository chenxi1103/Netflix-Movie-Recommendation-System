import sys
from flask import Flask
from RecommendModule import Model
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/recommend/<user_id>')
def inference(user_id):
    return m.predictForEachUser(str(user_id))

if __name__ == "__main__":
    configPath, expName = sys.argv[1], sys.argv[2]
    m = Model.ModelBasedModel(configPath, expName)
    m.loadModel()
    app.run(host='0.0.0.0', port=8082)
