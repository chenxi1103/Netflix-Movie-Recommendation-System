from flask import Flask
from flask import request
import requests
import time
import pandas as pd

from traffic_handlers import *
from state_handlers import *
from RouterTable import RouterTable
from eval_model import eval_model

model_status = "No_experiment"

app = Flask(__name__)
start_system()
ROUTER = RouterTable(BASE_PORT)
CONFIG_EXPERIMENTS = {}
TREATMENT_LOG = {'user_id': [], 'timestamp': []}
CONTROL_LOG = {'user_id': [], 'timestamp': []}

"""
On startup, we will evaluate Docker state and start a
Production container if necessary. It also terminates
with an error code if it cannot do so.
"""


@app.route('/')
def index():
    return "Welcome to the Movie Recommendation System!"


@app.route('/recommend/<user_id>')
def recommend(user_id):
    global CONFIG_EXPERIMENTS, TREATMENT_LOG, CONTROL_LOG
    global model_status

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
                # Test ends
                done = True
        elif CONFIG_EXPERIMENTS['DeploymentType'] == 'CanaryTest':
            start_time = CONFIG_EXPERIMENTS['StartTime']
            step = CONFIG_EXPERIMENTS['DeploymentParam']['Step']
            interval = CONFIG_EXPERIMENTS['DeploymentParam']['interval']
            percentage = (req_time - start_time) / interval * step
            if percentage > 1:
                # Test ends
                done = True
            else:
                # Change the percentage accordingly
                ROUTER.set_treat_percentage(percentage)
        if done:
            # Test ends
            global model_status
            isValid = eval_model(pd.DataFrame.from_dict(TREATMENT_LOG))
            if isValid:
                model_status = "Success"
                stop_test(is_successful=True)
            else:
                model_status = "Failed"
            TREATMENT_LOG = {'user_id': [], 'timestamp': []}
            CONTROL_LOG = {'user_id': [], 'timestamp': []}
            CONFIG_EXPERIMENTS = {}
            ROUTER.flush()
            # TODO: Shut down and open up containers accordingly
            # TODO: Calling email API

    if ROUTER.is_user_in_treatment(user_id):
        TREATMENT_LOG['user_id'].append(user_id)
        TREATMENT_LOG['timestamp'].append(req_time)
        return handle_test_traffic(user_id)
    else:
        CONTROL_LOG['user_id'].append(user_id)
        CONTROL_LOG['timestamp'].append(req_time)
        return handle_production_traffic(user_id)


@app.route('/test', methods=['GET', 'POST'])
def test():
    global CONFIG_EXPERIMENTS
    global model_status
    test_conf = request.json
    isSuccessful, config = parse_test_config(test_conf)
    print(config)
    if isSuccessful:
        CONFIG_EXPERIMENTS = config
        CONFIG_EXPERIMENTS['StartTime'] = time.time()
        cf.TEST_IMAGE = config["ModelInfo"]["ModelContainerName"]
        ROUTER.set_new_treatment(
            BASE_PORT + 2, config['ModelInfo']['ExpPercentage'] if 'ExpPercentage' in config['ModelInfo'] else 0)
        # ROUTER.set_new_treatment(BASE_PORT + 2, config['ModelInfo']['ExpPercentage'])
        global model_status
        model_status = "Pending"
        print(model_status)
        start_test(config["ModelInfo"]["ModelContainerName"],
                   8082, BASE_PORT + 2)
        print(config["ModelInfo"]["ModelContainerName"])
        return 'Test started successfully'
    else:
        return 'Test was not started, no changes have been applied'


@app.route('/model_status', methods=['GET'])
def jenkins_query():
    return model_status


@app.route('/reset_model_status', methods=['GET', 'POST'])
def reset_status():
    global model_status
    model_status = "No_experiment"
    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
