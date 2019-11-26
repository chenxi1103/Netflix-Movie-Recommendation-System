from flask import Flask, jsonify, render_template, request
import pymongo
import mongodb_client

app = Flask(__name__)
rate_table = mongodb_client.get_rate_table()

@app.route('/')
def monitor():
    return render_template('dashboard.html')


@app.route('/rate_data/', methods=['POST', 'GET'])
def get_rate():
    top_rate = get_top_rate(10)
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

if __name__ == '__main__':
    app.run(debug = True)
    get_top_rate(10)
