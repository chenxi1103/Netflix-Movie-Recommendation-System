import sys
import mongodb_client
import csv


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

if __name__ == '__main__':
    print(get_daily_watch_data(sys.argv[2]))
