import docker
IMAGE_NAME = 'teama/web-service:2'
LATEST_IMAGE_NAME = IMAGE_NAME
client = docker.from_env()

'''
This method starts a container based on the image parameter
It can be of the Image type, or a String value
A container object is returned on success, [] otherwise
'''


def start_and_get_containers(image):
    if not isinstance(image, str):
        image = image.tags[0]
    if check_container_status_and_get(image) == []:
        return client.containers.run(image=image, detach=True, ports={8082: 8082})
    else:
        return check_container_status_and_get(image)


'''
This method stops a container, taking the container object as an argument
returns True/False
'''


def stop_container(container):
    try:
        container.stop()
        return True
    except:
        return False


def check_container_status_and_get(container):
    if isinstance(container, str):
        return client.containers.list(filters={'ancestor': container})
    elif isinstance(container, Container):
        return client.containers.list(filters={'id': container.id})


def get_latest_image():
    try:
        return client.images.get(name=LATEST_IMAGE_NAME)
    except:
        return None


def main():
    # print(get_latest_image())
    container = start_and_get_containers(get_latest_image())
    print(container)
    print(stop_container(container[0]))


main()
