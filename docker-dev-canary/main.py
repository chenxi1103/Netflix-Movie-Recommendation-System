from flask import Flask
from flask import request
from traffic_handlers import *

import requests

app = Flask(__name__)

"""
This function will evaluate Docker state and start a
Production container if necessary. It also terminates
with an error code if it cannot do so.
"""
start_system()
print(TEST_REQUEST_COUNT)


@app.route('/')
def index():
    return "Welcome to the Movie Recommendation System!"


@app.route('/recommend/<user_id>')
def recommend(user_id):
    try:
        user_id = int(user_id)
    except:
        return 'Invalid user ID entered'

    # Simple production state, simply send all traffic to the production node
    if SYSTEM_STATE == 0:
        return handle_production_traffic(user_id)
    else:
        # Keep track of counter and stop here
        # Report, email
        TEST_REQUEST_COUNT += 1
        return handle_mixed_traffic(user_id)

    # TODO: somehow record this response
    # TODO: report(experimentType) -> boolean: isValid


@app.route('/test')
def test():
    test_conf = request.json
    if parse_test_config(test_conf):
        start_test(cf.LATEST_IMAGE_NAME, 8082, BASE_PORT + 2)
        return 'Test started successfully'
    else:
        return 'Test was not started, no changes have been applied'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
