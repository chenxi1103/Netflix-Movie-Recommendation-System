import sys
import mongodb_client
import csv

def summary_table(file_name, date):
    db = mongodb_client.get_former_table(date)
    with open(file_name, 'w') as file:
        csv_write = csv.writer(file)
        csv_head = ["user_id", "count"]
        csv_write.writerow(csv_head)
        for item in db.find():
            row_data = []
            row_data.append(item["user_id"])
            row_data.append(item["count"])
            csv_write.writerow(row_data)

if __name__ == '__main__':
    root = '/home/teama/17645TeamA/test_in_production/daily_query_summary/'
    date = sys.argv[1]
    file_name = root + date + ".csv"
    summary_table(file_name, date)
