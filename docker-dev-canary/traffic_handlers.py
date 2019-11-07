"""
This file has all traffic handling functions for the system
"""

import requests
from state_handlers import *

BASE_URL = 'http://128.2.204.234:'
PRODUCTION_PORT = '8081/'
TEST_PORT = '8083/'

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
            BASE_URL + PRODUCTION_PORT + 'recommend/' + str(user_id)).text
        return response
    except:
        return 'Invalid response from production prediction node'


def handle_test_traffic(user_id):
    try:
        response = requests.get(
            BASE_URL + TEST_PORT + 'recommend/' + str(user_id)).text
        return response
    except:
        return 'Invalid response from test prediction node'


def switch_traffic_ports_to_test():
    global PRODUCTION_PORT 
    global TEST_PORT
    PRODUCTION_PORT, TEST_PORT = TEST_PORT, PRODUCTION_PORT
