import sys
import json
from flask import Flask
sys.path.append('../inference')
sys.path.append('../inference/RecommendModule')
sys.path.append('../kafka_mongodb_process')
from RecommendModule import Model
import mongodb_client
from time import gmtime, strftime
import pickle

app = Flask(__name__)
table = mongodb_client.get_today_query_table()

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hi there! This is 17-645 Team A!</h1>"

@app.route('/recommend/<user_id>')
def inference(user_id):
    recommend_res = m.predictForEachUser(str(user_id))
    if not recommend_res:
        recommend_res = m.contentModel.getSimPopularMovie("-1")
    elif len(recommend_res) < 20:
        recommend_res.extend(m.contentModel.getSimPopularMovie(str(user_id)))
    movieid_list = movieid_adaptor(recommend_res)
    if len(movieid_list) > 20:
        movieid_list = movieid_list[:20]
    result = ','.join(movieid_list)
    movies = []
    
    for recommend_movies in recommend_res:
        movies.append(recommend_movies[0])
    update_table(user_id, movies)
    return result

def update_table(user_id, movies):
    query = {"user_id": user_id}
    result = table.find_one(query)
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if result is None:
        table.insert_one({"user_id": user_id, "movies": movies, "query_time": current_time})
    else:
        original = result["movies"]
        for movie in movies:
            if movie not in original:
                original.append(movie)
        newvalues = {"$set": {"movies": original, "query_time": current_time}}
        table.update_one(query, newvalues)

def movieid_adaptor(recommend_res):
    if not recommend_res:
        return recommend_res
    # content based recommendation
    res = []
    if len(recommend_res[0]) == 2:
        for i in recommend_res:
            if i[0] in tmidMovieIdDict:
                res.append(tmidMovieIdDict[i[0]])
    # collabrative filtering recommendation
    else:
        for i in recommend_res:
            if i in tmidMovieIdDict:
                res.append(tmidMovieIdDict[i])
    return res

if __name__ == "__main__":
    mainDir, expName = sys.argv[1], sys.argv[2]
    m = Model.ModelBasedModel(mainDir, expName)
    m.loadModel()
    with open("tmid2name.pkl", 'rb') as fp:
        tmidMovieIdDict = pickle.load(fp)

    app.run(host='0.0.0.0', port=8082)
