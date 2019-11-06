import sys
import json
import requests

if __name__=='__main__':
    exp_type, image_name = sys.argv[1], sys.argv[2]
    json_str = None
    if exp_type == 'Canary':
        with open("workflow/CanaryConfig.json",'r') as f:
            d = json.load(f)
            d["ModelInfo"]["ModelContainerName"] = image_name
            json_str = json.dumps(d) 
    elif exp_type == 'ABTest':
        with open("workflow/ABTestConfig.json",'r') as f:
            d = json.load(f)
            d["ModelInfo"]["ModelContainerName"] = image_name
            json_str = json.dumps(d) 
if json_str:
    r = requests.post('http://128.2.204.234:8082/test', json=json_str)
    print(r.status_code)

