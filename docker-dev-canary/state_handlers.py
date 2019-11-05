import sys
import container_functions as cf

# Default state is Production, indicated by 0
# 1 represents an ongoing test
SYSTEM_STATE = 0
PRODUCTION_BASE_URL = 'http://128.2.204.234:8082/'
current_containers = None


def is_any_running():
    return cf.check_container_status_and_get(cf.IMAGE_NAME) != None


def start_system():
    current_containers = cf.start_and_get_containers(
        cf.get_latest_image(), 8082, 8082)
    if current_containers == None:
        print('Critical error, system unable to start as no containers could be run')
        sys.exit(1)
    else:
        print('System has started successfully!')


def parse_ab_test_config(req):
    try:
        # Current state checking
        # Parse params
        duration = int(req.duration)
        # Create container, redirect traffic via map
        return True
    except:
        # State shall remain unchanged
        return False

        #     {
        #     "DeploymentId": "1",
        #     "DeploymentType": "A/BTest",
        #     "DeploymentParam": {
        #       "Duration": 135
        #     },
        #     "ModelInfo":
        #     [
        #       {
        #         "ModelContainerName": "container1",
        #         "UserRange": 0.2
        #       },
        #       {
        #         "ModelContainerName": "container2",
        #         "UserRange": 0.8
        #       }
        #     ]

        # }
