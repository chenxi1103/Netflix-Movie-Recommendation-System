#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-10-15
import unittest
import kafka_client
from unittest.mock import patch
import io
from kafka import KafkaProducer
from kafka import KafkaConsumer


# Mock API response with fixed JSON result
def mocked_requests_get_1(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0].startswith("http://128.2.204.215:8080/movie/"):
        return MockResponse({"id": "xxxxx"}, 200)
    elif args[0].startswith("http://128.2.204.215:8080/user/"):
        return MockResponse({"user_id": "12345"}, 200)


## Mock API response with invalid JSON format
def mocked_requests_get_2(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0].startswith("http://128.2.204.215:8080/movie/"):
        return MockResponse("xxxxx", 200)
    elif args[0].startswith("http://128.2.204.215:8080/user/"):
        return MockResponse("12345", 200)


class test_kafka_client(unittest.TestCase):
    def test_kafka_stream_validation(self):
        # Valid Case
        valid_kafka_msg = "2019-09-05T19:27:01,614,GET /data/m/brides+2004/20.mpg"
        kafka_client.kafka_stream_validation(valid_kafka_msg)

        # Invalid Case
        invalid_kafka_msg = "2019-09-05T19:27:01,614,GET,/data/m/brides+2004/20.mpg"
        self.assertRaises(AttributeError, kafka_client.kafka_stream_validation, invalid_kafka_msg)


    def test_parse_HTTP_request(self):
        # Valid Case
        valid_http_request = "GET /data/m/brides+2004/20.mpg"
        data = kafka_client.parse_HTTP_request(valid_http_request)
        assert data is not None
        # Invalid Case
        invalid_http_request_1 = "GET/data/m/brides+2004/20.mpg"
        invalid_http_request_2 = "     "
        self.assertRaises(AttributeError, kafka_client.parse_HTTP_request, invalid_http_request_1)
        self.assertRaises(AttributeError, kafka_client.parse_HTTP_request, invalid_http_request_2)

    def test_parse_detail_request(self):
        # Valid Case - Watch Data
        valid_watch_data = "/data/m/brides+2004/20.mpg"
        data = kafka_client.parse_detail_request(valid_watch_data)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[1], "data")
        self.assertEqual(data[2], "m")
        self.assertEqual(data[3], "brides+2004")
        self.assertEqual(data[4], "20.mpg")

        # Valid Case - Rate Data
        valid_rate_data = "/rate/grumpier+old+men+1995=3"
        data = kafka_client.parse_detail_request(valid_rate_data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[1], "rate")
        self.assertEqual(data[2], "grumpier+old+men+1995=3")

        # Invalid Case
        invalid_data_1 = "/rate/m/brides+2004/20.mpg"
        invalid_data_2 = "/data/grumpier+old+men+1995=3"
        invalid_data_3 = "///////"
        invalid_data_4 = "*******"
        self.assertRaises(AttributeError, kafka_client.parse_detail_request, invalid_data_1)
        self.assertRaises(AttributeError, kafka_client.parse_detail_request, invalid_data_2)
        self.assertRaises(AttributeError, kafka_client.parse_detail_request, invalid_data_3)
        self.assertRaises(AttributeError, kafka_client.parse_detail_request, invalid_data_4)

    def test_parse_chunk_number(self):
        # Valid Case
        valid_raw_data = "20.mpg"
        data = kafka_client.parse_chunk_number(valid_raw_data)
        self.assertEqual(data, 20)

        # Invalid Case
        invalid_raw_data_1 = "2&23.mpg"
        invalid_raw_data_2 = "."
        invalid_raw_data_3 = "*&^%"
        invalid_raw_data_4 = "-1.mpg"
        self.assertRaises(AttributeError, kafka_client.parse_chunk_number, invalid_raw_data_1)
        self.assertRaises(AttributeError, kafka_client.parse_chunk_number, invalid_raw_data_2)
        self.assertRaises(AttributeError, kafka_client.parse_chunk_number, invalid_raw_data_3)
        self.assertRaises(AttributeError, kafka_client.parse_chunk_number, invalid_raw_data_4)

    def test_extract_movie_id_and_rate(self):
        # Valid Case
        valid_raw_data = "grumpier+old+men+1995=3'"
        data = kafka_client.extract_movie_id_and_rate(valid_raw_data)
        self.assertEqual(data[0], "grumpier+old+men+1995")
        self.assertEqual(data[1], 3)

        invalid_raw_data_1 = "grumpier+old+men+1995=10'"
        invalid_raw_data_2 = "grumpier=xx'"
        invalid_raw_data_3 = "grumpier+old+men+1995/10'"
        self.assertRaises(AttributeError, kafka_client.extract_movie_id_and_rate, invalid_raw_data_1)
        self.assertRaises(AttributeError, kafka_client.extract_movie_id_and_rate, invalid_raw_data_2)
        self.assertRaises(AttributeError, kafka_client.extract_movie_id_and_rate, invalid_raw_data_3)

    def test_construct_watch_data(self):
        query_time = "2019-09-05T19:27:01"
        user_id = "614"
        movie_id = "12345"
        movie_name = "brides+2004"
        chunk_num = "20"
        data = kafka_client.construct_watch_data(query_time, user_id, movie_name, movie_id, chunk_num)
        self.assertEqual(data["query_time"], query_time)
        self.assertEqual(data["user_id"], user_id)
        self.assertEqual(data["movie_id"], movie_id)
        self.assertEqual(data["movie_name"], movie_name)
        self.assertEqual(data["chunk_num"], chunk_num)

    def test_construct_rate_data(self):
        query_time = "2019-09-05T19:27:01"
        user_id = "118106"
        movie_id = "12345"
        movie_name = "grumpier+old+men+1995"
        rate = "3"
        data = kafka_client.construct_rate_data(query_time, user_id, movie_name, movie_id, rate)
        self.assertEqual(data["query_time"], query_time)
        self.assertEqual(data["user_id"], user_id)
        self.assertEqual(data["movie_id"], movie_id)
        self.assertEqual(data["movie_name"], movie_name)
        self.assertEqual(data["score"], rate)

    def test_query_movie_api(self):
        # Valid case
        valid_movie_id = "brides+2004"
        result = kafka_client.query_movie_api(valid_movie_id)
        self.assertEqual(result["id"], valid_movie_id)

        # Invalid case
        invalid_movie_id_1 = "brides"
        invalid_movie_id_2 = "xxxxx"
        invalid_movie_id_3 = "+2004"
        self.assertRaises(AttributeError, kafka_client.query_movie_api, invalid_movie_id_1)
        self.assertRaises(AttributeError, kafka_client.query_movie_api, invalid_movie_id_2)
        self.assertRaises(AttributeError, kafka_client.query_movie_api, invalid_movie_id_3)

    @patch('requests.get', side_effect=mocked_requests_get_1)
    def test_mock_query_movie_api_1(self, mock_get):
        mocked_query_result = {"id": "xxxxx"}
        mock_result = kafka_client.query_movie_api("xxxxx")
        self.assertEqual(mocked_query_result, mock_result)
        self.assertRaises(AttributeError, kafka_client.query_movie_api, "xxxxssss")

    @patch('requests.get', side_effect=mocked_requests_get_2)
    def test_mock_query_movie_api_2(self, mock_get):
        self.assertRaises(AttributeError, kafka_client.query_movie_api, "xxxxx")

    def test_query_user_api(self):
        # Valid case
        valid_user_id = '111'
        result = kafka_client.query_user_api(valid_user_id)
        self.assertEqual(str(result['user_id']), valid_user_id)

        # Invalid case
        invalid_user_id_1 = "123321123321"
        invalid_user_id_2 = "sdfsdfsdf"
        invalid_user_id_3 = "-1"
        self.assertRaises(AttributeError, kafka_client.query_user_api, invalid_user_id_1)
        self.assertRaises(AttributeError, kafka_client.query_user_api, invalid_user_id_2)
        self.assertRaises(AttributeError, kafka_client.query_user_api, invalid_user_id_3)

    @patch('requests.get', side_effect=mocked_requests_get_1)
    def test_mock_query_user_api_1(self, mock_get):
        mocked_query_result = {'user_id': '12345'}
        mock_result = kafka_client.query_user_api('12345')
        self.assertEqual(mocked_query_result, mock_result)
        self.assertRaises(AttributeError, kafka_client.query_user_api, "xxxxssss")

    @patch('requests.get', side_effect=mocked_requests_get_2)
    def test_mock_query_user_api_2(self, mock_get):
        self.assertRaises(AttributeError, kafka_client.query_user_api, "xxxxx")

    def test_parse_msg_value(self):
        # Valid case
        valid_data_1 = "b'2019-09-05T19:27:01,614,GET /data/m/brides+2004/20.mpg'"
        valid_data_2 = "b'2019-09-05T19:27:01,118106,GET /rate/grumpier+old+men+1995=3'"
        kafka_client.parse_msg_value(valid_data_1)
        kafka_client.parse_msg_value(valid_data_2)

        # Invalid case
        invalid_data_1 = "2019-09-05T19:27:01,614,GET/data/m/brides+2004/20.mpg'"
        invalid_data_2 = "2019-09-05T19:27:01/614/GET/data/m/brides+2004/20.mpg'"
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            kafka_client.parse_msg_value(invalid_data_1)
        self.assertEqual(mock_stdout.getvalue(),
                         'Information of user whose user_id is 614 has already recorded in database.\nInvalid HTTP request.\n')

        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            kafka_client.parse_msg_value(invalid_data_2)
        self.assertEqual(mock_stdout.getvalue(), "kafka stream data schema is not valid. (Does not follow 'Timestamp,user_id,HTTP_query_info' schema\n")

    def test_write_user_info(self):
        # Valid case
        valid_user_id = '100'
        kafka_client.write_user_info(valid_user_id)

        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            kafka_client.write_user_info(valid_user_id)
        self.assertEqual(mock_stdout.getvalue(),
                         "Information of user whose user_id is {0} has already recorded in database.\n".format(
                             valid_user_id))
        # Invalid case
        invalid_user_id = 'xxx'
        self.assertRaises(AttributeError, kafka_client.write_user_info, invalid_user_id)

    def test_write_movie_info(self):
        # Valid case
        valid_movie_id = "grumpier+old+men+1995"
        kafka_client.write_movie_info(valid_movie_id)
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            kafka_client.write_movie_info(valid_movie_id)
        self.assertEqual(mock_stdout.getvalue(),
                         "Information of movie whose movie_id is {0} has already recorded in database.\n".format(
                             valid_movie_id))

        # Invalid case
        self.assertRaises(AttributeError, kafka_client.write_movie_info, None)

    def test_write_rate_data(self):
        # Valid case
        movie_id = 'grumpier+old+men+1995'
        user_id = '118106'
        query_time = '2019-09-05T19:27:01'
        score = '3'

        kafka_client.write_rate_data(movie_id, query_time, user_id, score)
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            kafka_client.write_rate_data(movie_id, query_time, user_id, '5')
        self.assertEqual(mock_stdout.getvalue(),
                         "User {0} score to movie {1} has updated to {2}\n".format(user_id, movie_id, '5'))

        # #Invalid case
        # invalid_movie_id = "xxxx"
        # self.assertRaises(AttributeError, kafka_client.write_rate_data, invalid_movie_id, query_time, user_id, score)

    def test_kafka(self):
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
        producer.send('test', key=b'test_key', value=b'test_value', partition=0)
        producer.close()
        consumer = KafkaConsumer('test', group_id='group1', bootstrap_servers=['localhost:9092'],
                                 api_version=(0, 10))
        for msg in consumer:
            self.assertEqual(msg.key, b'test_key')
            self.assertEqual(msg.value, b'test_value')
            consumer.close()
            break
