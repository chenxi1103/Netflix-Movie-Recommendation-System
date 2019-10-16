import sys
from flask import Flask
sys.path.append('/home/teama/17645TeamA/inference')
from RecommendModule import Model
import mongodb_client

app = Flask(__name__)
table = mongodb_client.get_table()

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/recommend/<user_id>')
def inference(user_id):
    update_table(user_id)
    return str(m.predictForEachUser(str(user_id)))

def update_table(user_id):
    query = {"user_id": user_id}
    result = table.find_one(query)
    if result is None:
        table.insert_one({"user_id": user_id, "count": 1})
    else:
        newvalues = {"$set": {"count": int(result["count"]) + 1}}
        table.update_one(query, newvalues)

if __name__ == "__main__":
    mainDirPath, configPath, expName = sys.argv[1], sys.argv[2], sys.argv[3]
    m = Model.ModelBasedModel(mainDirPath, configPath, expName)
    m.loadModel()
    app.run(host='0.0.0.0', port=8082)
