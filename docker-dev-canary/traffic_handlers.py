"""
This file has all traffic handling functions for the system
"""

import requests
from state_handlers import *

PRODUCTION_BASE_URL = 'http://128.2.204.234:8081/'
TEST_BASE_URL = 'http://128.2.204.234:8083/'
TEST_REQUEST_COUNT = 0

"""
Returns 0 if the user needs to be redirected to the production 
server, otherwise returns 1
"""


def is_user_production(user_id):
    return True


def handle_mixed_traffic(user_id):
    if is_user_production(user_id):
        return handle_production_traffic(user_id)
    else:
        return handle_test_traffic(user_id)


def handle_production_traffic(user_id):
    try:
        response = requests.get(
            PRODUCTION_BASE_URL + 'recommend/' + str(user_id)).text
        return response
    except:
        return 'Invalid response from production prediction node'


def handle_test_traffic(user_id):
    try:
        response = requests.get(
            TEST_BASE_URL + 'recommend/' + str(user_id)).text
        return response
    except:
        return 'Invalid response from production prediction node'
