import sys
import requests
import time
hostname = "http://128.2.204.234"
port = "8082"

def reset_status():
    url = hostname + ":" + port + "/reset_model_status"
    requests.post(url)

if __name__=='__main__':
    url = hostname + ":" + port + "/model_status"
    response = requests.get(url)
    status = str(response.content.decode("utf-8"))
    print(status)
    report = ""
    if status == "No_experiment":
        report = "Supervisor Error. No experiment detected!"
        print(report)
        sys.exit(1)
    counter = 0
    while status == "Pending":
        if counter <= 100:
            status = str(requests.get(url).content.decode("utf-8"))
            print('Pending')
            if status == "Success":
                report = "Model evaluation success! Model is ready to release!"
                print(report)
                reset_status()
                sys.exit(0)
            if status == "Failed":
                report = "Model evaluation failed! Model is going to rollback!"
                print(report)
                reset_status()
                sys.exit(1)
            counter += 1
            time.sleep(10)
        else:
            break
    if status == "Pending" or status == "No_experiment" or status == "Failed":
        report = "Runtime Error! Model Evaluation failed! Model is going to rollback!"
        print(report)
        reset_status()
        sys.exit(1)
    else:
        report = "Model evaluation success! Model is ready to release!"
        print(report)
        reset_status()
        sys.exit(0)


