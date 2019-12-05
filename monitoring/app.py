from flask import Flask, jsonify, render_template, request
import json
import pymongo
import os
import mongodb_client
import csv
import FeedbackLoopUtil

app = Flask(__name__)
rate_table = mongodb_client.get_rate_table()
beta_table = mongodb_client.get_beta_table()
alpha_table = mongodb_client.get_alpha_table()
charlie_table = mongodb_client.get_charlie_table()
top_rate = {}
realtime_attack = []
batch_attack = []

feedback_loop = FeedbackLoopUtil.FeedbackLoopUtil('monitor-service')


@app.route('/')
def monitor():
    return render_template('index.html')


@app.route('/monitor/', methods=['POST', 'GET'])
def get_rate():
    top_rate = get_top_rate(10)
    alpha, beta, charlie = get_top_recommend(5)
    with open("static/data/difference_score.json", "r") as file:
        differece_score = json.loads(file.readline())

    global realtime_attack
    global batch_attack
    if len(realtime_attack) == 0:
        realtime_flag = "N"
    else:
        realtime_flag = "Y"

    if len(batch_attack) == 0:
        batch_flag = "N"
    else:
        batch_flag = "Y"
    return render_template('dashboard.html', data={'top_rate': top_rate, 'difference_score': differece_score,
                                                   'alpha': alpha, 'beta': beta, 'charlie': charlie,
                                                   'realtime_attack': realtime_attack, 'batch_attack': batch_attack,
                                                   'realtime_flag': realtime_flag, 'batch_flag': batch_flag})

@app.route('/attack_update/', methods=['POST', 'GET'])
def attack_update():
    res = request.json
    print(res)
    messages = res['messages']
    type = res['type']
    if len(messages) > 0 and type == 'realtime':
        global realtime_attack
        realtime_attack = messages
    elif len(messages) > 0 and type == 'batch':
        global batch_attack
        batch_attack = messages
    print('[Attack Detector]server side print:', res)
    return get_rate()

@app.route('/feedback_update/', methods=['POST', 'GET'])
def feedback_update():
    res = feedback_loop.monitor_process(request.json)
    print('server side print:',res)
    res = json.loads(res)
    with open("static/data/difference_score.json", "r") as file:
        differece_score = json.loads(file.readline())

    if 'alpha' in res:
        teama = res['alpha']
        with open('static/data/data_a.tsv', 'w') as file:
            tsv_writer = csv.writer(file, delimiter='\t')
            tsv_writer.writerow(['letter', 'frequency'])
            for gerne in teama['ratio']:
                tsv_writer.writerow([gerne, str(teama['ratio'][gerne])])
        differece_score['teama'] = teama['difference_score']

    if 'beta' in res:
        teamb = res['beta']
        with open('static/data/data_b.tsv', 'w') as file:
            tsv_writer = csv.writer(file, delimiter='\t')
            tsv_writer.writerow(['letter', 'frequency'])
            for gerne in teamb['ratio']:
                tsv_writer.writerow([gerne, str(teamb['ratio'][gerne])])
        differece_score['teamb'] = teamb['difference_score']

    if 'charlie' in res:
        teamc = res['charlie']
        with open('static/data/data_c.tsv', 'w') as file:
            tsv_writer = csv.writer(file, delimiter='\t')
            tsv_writer.writerow(['letter', 'frequency'])
            for gerne in teamc['ratio']:
                tsv_writer.writerow([gerne, str(teamc['ratio'][gerne])])
        differece_score['teamc'] = teamc['difference_score']

    with open("static/data/difference_score.json", "w") as file:
        file.write(json.dumps(differece_score))
    return get_rate()


def get_top_rate(k):
    counter = 0
    result = []
    for x in rate_table.find().sort("_id", -1):
        counter = counter + 1
        if counter <= k:
            result.append(x)
        else:
            break
    return result


def get_top_recommend(k):
    counter = 0
    beta = []
    alpha = []
    charlie = []

    for x in beta_table.find().sort("_id", -1):
        counter = counter + 1
        if counter <= k:
            beta.append(x)
        else:
            break

    counter = 0
    for x in alpha_table.find().sort("_id", -1):
        counter = counter + 1
        if counter <= k:
            alpha.append(x)
        else:
            break

    counter = 0
    for x in charlie_table.find().sort("_id", -1):
        counter = counter + 1
        if counter <= k:
            charlie.append(x)
        else:
            break
    return alpha, beta, charlie

if __name__ == '__main__':
    if not os.path.exists("static/data/difference_score.json"):
        differece_score = {"teama": 0, "teamb": 0, "teamc": 0}
        with open("static/data/difference_score.json", "w") as file:
            file.write(json.dumps(differece_score))
    app.run(debug=True, host='0.0.0.0')
    get_top_rate(10)

