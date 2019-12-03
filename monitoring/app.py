from flask import Flask, jsonify, render_template, request
import pymongo
import mongodb_client
import csv
import FeedbackLoopUtil


app = Flask(__name__)
rate_table = mongodb_client.get_rate_table()
beta_table = mongodb_client.get_beta_table()
alpha_table = mongodb_client.get_alpha_table()
charlie_table = mongodb_client.get_charlie_table()
top_rate = {}
feedback_loop = FeedbackLoopUtil.FeedbackLoopUtil('monitor-service')


@app.route('/')
def monitor():
    return render_template('dashboard.html')


@app.route('/rate_data/', methods=['POST', 'GET'])
def get_rate():
    top_rate = get_top_rate(10)
    alpha, beta, charlie = get_top_recommend(5)
    return render_template('dashboard.html', data={'top_rate': top_rate, 'alpha': alpha, 'beta': beta, 'charlie': charlie})

@app.route('/write_genre_freq/', methods=['POST'])
def write_genre_freq():
    freqs = request.get_json()
    with open('static/data/data.tsv', 'w') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        tsv_writer.writerow(['letter', 'frequency'])
        for gerne in freqs:
            tsv_writer.writerow([gerne, str(freqs[gerne])])
    return render_template('dashboard.html', data={'top_rate': top_rate})

def get_top_rate(k):
    counter = 0
    result = []
    for x in rate_table.find().sort("_id",-1):
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

    for x in beta_table.find().sort("_id",-1):
        counter = counter + 1
        if counter <= k:
            beta.append(x)
        else:
            break

    counter = 0
    for x in alpha_table.find().sort("_id",-1):
        counter = counter + 1
        if counter <= k:
            alpha.append(x)
        else:
            break

    counter = 0
    for x in charlie_table.find().sort("_id",-1):
        counter = counter + 1
        if counter <= k:
            charlie.append(x)
        else:
            break
    return alpha, beta, charlie

@app.route('/feedback_update/', methods=['POST', 'GET'])
def feedback_update():
    res = feedback_loop.monitor_process(request.json)
    print('server side print:',res)
    return res

@app.route('/attack_update/', methods=['POST', 'GET'])
def attack_update():
    res = request.json
    print('[Attack Detector]server side print:', res)
    return 'Something from /attack_update'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    get_top_rate(10)
