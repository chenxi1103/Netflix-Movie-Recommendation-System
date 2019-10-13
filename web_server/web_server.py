import sys
from flask import Flask
app = Flask(__name__)

def load_artifect(config_path):
    pass

def user_distribution(user_id, ABtest_config):
    model_name = "abc"
    return model_dict[model_name]

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/recommend/<user_id>')
def inference(user_id):
    return str(int(user_id) + 1 + model_dict["abc"])

if __name__ == "__main__":
    config_path = sys.argv[1]
    print(config_path)
    model_dict = {"abc":123,"edf":456}
    load_artifect(config_path="abc")
    app.run(host='0.0.0.0', port=8082)
