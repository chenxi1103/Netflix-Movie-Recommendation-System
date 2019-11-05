import docker

IMAGE_NAME = 'teama/web-service'
LATEST_IMAGE_NAME = IMAGE_NAME + ':latest'
client = docker.from_env()

"""
This method starts a container based on the image parameter
It can be of the Image type, or a String value
It will either return the list of running containers matching
the image, or a list with one Container if a new one was started.
or None if the image passed was None
"""


def start_and_get_containers(image, host_port, container_port):
    if image is None:
        return []
    if not isinstance(image, str):
        image = image.tags[0]
    if check_container_status_and_get(image) == []:
        return [client.containers.run(image=image, detach=True, ports={host_port: container_port})]
    else:
        return check_container_status_and_get(image)


"""
This method stops a container, taking the container object as an argument
returns True/False
"""


def stop_container(container):
    try:
        container.stop()
        return True
    except:
        return False


"""
This method checks the state of the containers, and returns a list of containers
Otherwise, it returns None
"""


def check_container_status_and_get(containerImage):
    if isinstance(containerImage, str):
        list_containers = client.containers.list(
            filters={'ancestor': containerImage})
        return None if list_containers == [] else list_containers
    elif isinstance(containerImage, Container):
        list_containers = client.containers.list(
            filters={'id': containerImage.id})
        return None if list_containers == [] else list_containers


"""
Returns the latest image from the Docker registry
"""


def get_latest_image():
    try:
        return client.images.get(name=LATEST_IMAGE_NAME)
    except:
        return None
