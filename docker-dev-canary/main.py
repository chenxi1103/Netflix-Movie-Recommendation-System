from flask import Flask
from flask import request
from state_handlers import *
from traffic_handlers import *

import requests

app = Flask(__name__)

# This function will evaluate Docker state and start a
# Production container if necessary. It also terminates
# with an error code if it cannot do so.
start_system()


@app.route('/')
def index():
    return "Welcome to the Movie Recommendation System!"


@app.route('/recommend')
def recommend():
    try:
        user_id = int(request.args.get('user_id'))
    except:
        return 'Invalid user ID entered'

    # Simple production state, simply send all traffic to the production node
    if SYSTEM_STATE == 0:
        return handle_production_traffic(user_id)

    return user_id


@app.route('/abtest')
def ab_test():
    ab_test_conf = request.json
    if parse_ab_test_config(ab_test_conf):
        return 'Test started successfully'
    else:
        return 'Test was not started, no changes have been applied'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
