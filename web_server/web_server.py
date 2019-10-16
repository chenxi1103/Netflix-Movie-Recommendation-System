import sys
import json
from flask import Flask
sys.path.append('../inference')
sys.path.append('../inference/RecommendModule')
sys.path.append('../kafka_mongodb_process')
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
    recommend_res = m.predictForEachUser(str(user_id))
    if not recommend_res:
        recommend_res = m.contentModel.getSimPopularMovie("-1")
    elif len(recommend_res) < 20:
        recommend_res.extend(m.contentModel.getSimPopularMovie(str(user_id)))
    return json.dumps(recommend_res)

def update_table(user_id):
    query = {"user_id": user_id}
    result = table.find_one(query)
    if result is None:
        table.insert_one({"user_id": user_id, "count": 1})
    else:
        newvalues = {"$set": {"count": int(result["count"]) + 1}}
        table.update_one(query, newvalues)

if __name__ == "__main__":
    mainDir, expName = sys.argv[1], sys.argv[2]
    m = Model.ModelBasedModel(mainDir, expName)
    m.loadModel()
    app.run(host='0.0.0.0', port=8082)
