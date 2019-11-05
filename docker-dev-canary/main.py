from flask import Flask
from flask import request
import requests
import time
import pandas as pd

from traffic_handlers import *
from state_handlers import *
from RouterTable import RouterTable
from eval_model import eval_model


app = Flask(__name__)

"""
This function will evaluate Docker state and start a
Production container if necessary. It also terminates
with an error code if it cannot do so.
"""
start_system()
# print(TEST_REQUEST_COUNT)
ROUTER = RouterTable(BASE_PORT)
CONFIG_EXPERIMENTS = {}
EXPERIMENT_LOG = {'user_id': [], 'timestamp': []}


@app.route('/')
def index():
    return "Welcome to the Movie Recommendation System!"


@app.route('/recommend/<user_id>')
def recommend(user_id):
    global CONFIG_EXPERIMENTS, EXPERIMENT_LOG
    try:
        user_id = int(user_id)
    except:
        return 'Invalid user ID entered'

    req_time = time.time()

    # If an experiment is ongoing
    if len(CONFIG_EXPERIMENTS) > 0:
        done = False
        if CONFIG_EXPERIMENTS['DeploymentType'] == 'A/BTest':
            duration = CONFIG_EXPERIMENTS['Duration']
            if req_time - CONFIG_EXPERIMENTS['StartTime'] >= duration:
                # Test ends.
                done = True
        elif CONFIG_EXPERIMENTS['DeploymentType'] == 'CanaryTest':
            start_time = CONFIG_EXPERIMENTS['StartTime']
            step = CONFIG_EXPERIMENTS['Step']
            interval = CONFIG_EXPERIMENTS['interval']
            percentage = (req_time - start_time) / interval * step
            if percentage > 1:
                # Test ends
                done = True
            else:
                # Change the percentage accordingly
                ROUTER.set_treat_percentage(percentage)
        if done:
            # Test ends.
            isValid = eval_model(pd.DataFrame.from_dict(EXPERIMENT_LOG))
            EXPERIMENT_LOG = {'user_id': [], 'timestamp': []}
            CONFIG_EXPERIMENTS = {}
            ROUTER.flush()
            # TODO: Shut down and open up containers accordingly
            # TODO: Calling email API

    if ROUTER.is_user_in_treatment(user_id):
        EXPERIMENT_LOG['user_id'].append(user_id)
        EXPERIMENT_LOG['timestamp'].append(req_time)
        return handle_test_traffic(user_id)
    else:
        return handle_production_traffic(user_id)


@app.route('/test', methods=['GET', 'POST'])
def test():
    global CONFIG_EXPERIMENTS
    test_conf = request.json
    isSuccessful, config = parse_test_config(test_conf)
    if isSuccessful:
        CONFIG_EXPERIMENTS = config
        CONFIG_EXPERIMENTS['StartTime'] = time.time()
        ROUTER.set_new_treatment(BASE_PORT + 2, config['ModelInfo']['ExpPercentage'])
        start_test(config["ModelInfo"]["ModelContainerName"], 8082, BASE_PORT + 2)
        print(config["ModelInfo"]["ModelContainerName"])
        return 'Test started successfully'
    else:
        return 'Test was not started, no changes have been applied'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
