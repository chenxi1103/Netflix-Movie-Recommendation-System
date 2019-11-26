import pandas as pd
from scipy import stats

"""
This function takes the data that a specific model produces and tell whether it is a good model or not.

Parameters:
    df: The data that a particular model produces. It should contains following columns.
        user_id: The id of the user.
        response: The recommendation that we give back.
        timestamp: The timestamp of the request. (or response)
    req_percentage: Over this threshold, the model is successful.
    time_window: The time window that a user come back. This is in minutes.
Return: boolean. Determine whether certain percentages of users use the recommendation again in a time window.
"""
def eval_model(df, req_percentage=0.5, time_window=20):
    total_requests = df.shape[0]
    return (num_following_req(df, time_window) / total_requests + 1) >= req_percentage

def percentage_following_req(df, time_window):
    total_requests = df.shape[0]
    return num_following_req(df, time_window) / total_requests

def t_test(df_control, df_treatment, time_window=20):
    control = get_one_hot_list(df_control, time_window)
    treatment = get_one_hot_list(df_treatment, time_window)
    return stats.ttest_ind(control, treatment)[1]

def get_one_hot_list(df, time_window=20):
    time_window *= 60
    l = []
    for user_id, group in df.groupby('user_id'):
        timestamps = group['timestamp'].tolist()
        for i in range(1, len(timestamps)):
            if (timestamps[i] - timestamps[i-1] <= time_window):
                l.append(1)
            else:
                l.append(0)
    return l

"""
Return the number of requests that are in the time_window of the last request. This can be included in our report.
"""
def num_following_req(df, time_window=20):
    time_window *= 60
    count_successful = 0
    for user_id, group in df.groupby('user_id'):
        timestamps = group['timestamp'].tolist()
        for i in range(1, len(timestamps)):
            if (timestamps[i] - timestamps[i-1] <= time_window):
                count_successful += 1
    return count_successful

# if __name__ == "__main__":
#     data = {'user_id': [1, 2, 3, 4, 1, 1, 3, 5, 2], 'timestamp': [1, 8, 10, 20, 23, 26, 29, 50, 88]}
#     df = pd.DataFrame.from_dict(data)
#     print(eval_model(df, 0.2, 20))
