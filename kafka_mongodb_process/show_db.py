#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-10-12
import mongodb_client
movie_table = mongodb_client.get_movie_table()
user_table = mongodb_client.get_user_table()
stream_watch_table = mongodb_client.get_watch_table()
stream_rate_table = mongodb_client.get_rate_table()

def show_movie_table():
    counter = 0
    for x in movie_table.find():
        print(x)
        counter = counter + 1
        if counter > 100:
            break

def show_user_table():
    counter = 0
    for x in user_table.find():
        print(x)
        counter = counter + 1
        if counter > 100:
            break


def show_watch_table():
    counter = 0
    for x in stream_watch_table.find():
        counter = counter + 1
        if counter < 100:
            print(x)
    print("watch table length: ", counter)


def show_rate_table():
    counter = 0
    for x in stream_rate_table.find():
        print(x)
        counter = counter + 1
        if counter > 100:
            break


if __name__ == '__main__':
    print("============== Movie Table ==============")
    show_movie_table()
    print("============== User Table ==============")
    show_user_table()
    print("============== Watch Table ==============")
    show_watch_table()
    print("============== Rate Table ==============")
    show_rate_table()
