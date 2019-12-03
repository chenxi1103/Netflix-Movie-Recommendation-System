from flask import Flask, jsonify, render_template, request
import pymongo
import mongodb_client
import csv

app = Flask(__name__)
rate_table = mongodb_client.get_rate_table()
beta_table = mongodb_client.get_beta_table()
alpha_table = mongodb_client.get_alpha_table()
charlie_table = mongodb_client.get_charlie_table()
top_rate = {}


@app.route('/')
def monitor():
    return render_template('index.html')


@app.route('/monitor/', methods=['POST', 'GET'])
def get_rate():
    top_rate = get_top_rate(10)
    alpha, beta, charlie = get_top_recommend(5)
    difference_score = {}
    with open('static/data/difference_score.txt', 'r') as file:
        difference_score['teama'] = file.readline().strip("\n")
        difference_score['teamb'] = file.readline().strip("\n")
        difference_score['teamc'] = file.readline()
    return render_template('dashboard.html', data={'top_rate': top_rate, 'difference_score': difference_score,
                                                   'alpha': alpha, 'beta': beta, 'charlie': charlie})


@app.route('/write_genre_freq/', methods=['POST'])
def write_genre_freq():
    freqs = request.get_json()
    teama = freqs['teama']
    teamb = freqs['teamb']
    teamc = freqs['teamc']
    with open('static/data/data_a.tsv', 'w') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        tsv_writer.writerow(['letter', 'frequency'])
        for gerne in teama['ratio']:
            tsv_writer.writerow([gerne, str(teama['ratio'][gerne])])
    with open('static/data/data_b.tsv', 'w') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        tsv_writer.writerow(['letter', 'frequency'])
        for gerne in teamb['ratio']:
            tsv_writer.writerow([gerne, str(teamb['ratio'][gerne])])
    with open('static/data/data_c.tsv', 'w') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        tsv_writer.writerow(['letter', 'frequency'])
        for gerne in teamc['ratio']:
            tsv_writer.writerow([gerne, str(teamc['ratio'][gerne])])
    with open('static/data/difference_score.txt', 'w') as file:
        file.write(str(teama['difference_score']) + "\n")
        file.write(str(teamb['difference_score']) + "\n")
        file.write(str(teamc['difference_score']))
    return render_template('dashboard.html', data={'top_rate': top_rate})


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
    app.run(debug=True, host='0.0.0.0')
    get_top_rate(10)
