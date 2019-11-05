"""
This file has all traffic handling functions for the system
"""

import requests

PRODUCTION_BASE_URL = 'http://128.2.204.234:8082/'


def handle_production_traffic(user_id):
    try:
        response = requests.get(
            PRODUCTION_BASE_URL + 'recommend/' + str(user_id)).text
        return response
    except:
        return 'Invalid response from production prediction node'
