import sys
import mongodb_client
from datetime import datetime, timedelta
import csv

def write_result_to_csv(date, delta, file_name):
    with open(file_name, 'w') as file:
        csv_write = csv.writer(file)
        csv_head = ["date", "delta", "hit_rate"]
        csv_write.writerow(csv_head)
        rate = get_hit_rate(date, delta)
        row = []
        row.append(date)
        row.append(delta)
        row.append(rate)
        csv_write.writerow(row)

def get_daily_query_data(date):
    table = mongodb_client.get_former_query_table(date)
    result = []
    for item in table.find():
        result.append(item)
    return result


def get_daily_watch_data(date):
    table = mongodb_client.get_daily_summary_watch_table(date)
    result = []
    for item in table.find():
        result.append(item)
    return result


def get_hit_rate(date, delta):
    target_date = datetime.strptime(date, '%Y-%m-%d')
    recommend_movies_count = get_total_recommend_movies(date)
    watch_movies_count = 0
    for i in range(0, delta):
        watch_date = datetime.strftime(target_date + timedelta(i + 1), '%Y-%m-%d')
        watch_movies_count += get_total_hit(date, str(watch_date))
    return watch_movies_count / recommend_movies_count


def get_total_recommend_movies(date):
    result = get_daily_query_data(date)
    count = 0
    for entry in result:
        count += len(entry["movies"])
    return count


def summary_watch_data(watch_date):
    watch_data = get_daily_watch_data(watch_date)
    result = {}
    for entry in watch_data:
        user_id = entry["user_id"]
        if user_id in result:
            result[user_id].append(str(entry["movie_id"]))
        else:
            result[user_id] = []
            result[user_id].append(str(entry["movie_id"]))
    return result


def get_total_hit(query_date, watch_date):
    query_data = get_daily_query_data(query_date)
    watch_data = summary_watch_data(watch_date)
    count = 0
    for entry in query_data:
        user_id = entry["user_id"]
        recommend_movies = entry["movies"]
        if user_id in watch_data:
            watched_movies = watch_data[user_id]
            for movie in watched_movies:
                if movie in recommend_movies:
                    count = count + 1
    return count


if __name__ == '__main__':
    root = '/home/teama/17645TeamA/test_in_production/daily_query_summary/'
    date = sys.argv[1]
    delta = int(sys.argv[2])
    write_result_to_csv(date, delta, root + date + "_with_delta_" + str(delta) + ".csv")
