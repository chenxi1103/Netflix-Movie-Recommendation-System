import sys
import requests
import time
hostname = "http://128.2.204.234"
port = "8082"

if __name__=='__main__':
    url = hostname + ":" + port + "/model_status"
    response = requests.get(url)
    status = response.content()
    report = ""
    if status == "No_experiment":
        report = "Supervisor Error. No experiment detected!"
        sys.exit(1)
    counter = 0
    while status == "Pending":
        if counter <= 100:
            status = requests.get(url).content()
            if status == "Success" or "Failed":
                report = "Model evaluation success! Model is ready to release!"
                sys.exit(0)
            if status == "Failed":
                report = "Model evaluation failed! Model is going to rollback!"
                sys.exit(1)
            counter += 1
            time.sleep(600)
        else:
            break
    if status == "Pending" or status == "No_experiment" or status == "Failed":
        report = "Runtime Error! Model Evaluation failed! Model is going to rollback!"
        sys.exit(1)
    else:
        report = "Model evaluation success! Model is ready to release!"
        sys.exit(0)


