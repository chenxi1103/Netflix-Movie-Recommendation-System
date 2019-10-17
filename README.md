# 17645TeamA
## Code Structure Overview
![alt text](https://github.com/chenxi1103/17645TeamA/blob/master/README_img/CodeStructure.png "Project Code Structure")

Our recommendation system consists of five modules. 

**KafkaProcessingModule** receives, processes Kafka stream and stores data in MongoDB.

**FeatureExtractionModule** retrieves, transforms data from MongoDB according to FeatureExtractionConfig to features. Then it stores the features in the FeatureStoreFolder. 

The above two models inspect the data format or semantic to ensure data quality. 

**Offline Recommend Training Module** retrieves feature from feature store folder and trains the model. It also evaluates the model performance offline and stores the model with evaluation results in model management folder. The hyperparameter or model path are all configured in offline training configuration.  

**Online prediction module** provides online recommendation results given userid. It is within webserver and responds to external API. It loads and manages trained model according to the online deployment configuration. 

**Production Test module** obtains data from both Kafka stream and Online Prediction Module. 

All five models are tested for infrastructure quality. 

## Data Quality

To ensure data is absolutely clean before it can be used to train the model, we do “double check” data cleaning both in “Kafka streaming” part and “feature extraction” part. <br>

### Kafka Streaming

For “Kafka streaming” part, it is very important to ensure that the data queried from Kafka topic follows the correct schema. There are two types of ConsumerRecord here. One is watch data which represents the information of a user watch a movie and it follows the schema like:"[TimeStamp],[user_id],GET /data/m/[movie_id]/[block_num].mpg"
The other is rate data which represent the information of how a user rate a movie and it follows the schema like:"[TimeStamp],[user_id],GET /rate/[movie_id]=[score]."<br>

For both watch and rate data, they can be split into 3 pieces by comma. So first we check if this data can be split into exactly 3 piece by comma. [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L45-L52) And we also check if user_id is a numeric string [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L174-L186). Then we check the third piece, which is the most important part. For watch data, it can be split into 5 pieces by “/“ while for rate data it can be split into 3 pieces by “/“. So if the third piece neither can be split into 3 nor 5 pieces, it is invalid [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L66-L91). If the third piece is split into 5 pieces, we should then make sure the second block is exactly “data” [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L66-L91). And if the third piece is split into 3 pieces, we should then make sure the second block is exactly “rate” [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L66-L91). After that, we can extract movie_id out and check if it is not None [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L232-L243). For watch data, we can further extract block_num out. We then check if block_num is a non-negative numeric string[[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L93-L107). For rate data, the movie_id and score can be extracted by splitting last piece by “=“. If splitting result is not two pieces, it is invalid [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L109-L121). Then we further check if score is a numeric string within range 0 to 5 [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L109-L121).  <br>

After extract useful information from Kafka raw streaming data, we also do lots of check before writing them into database. There are four tables in database. One is for user information, one is for movie information, one is for watch data, and one is for rate data. After extract a user_id out, we first check if the user_data table has already had the record for this user. If yes, we do nothing. If no, we query the API and insert a new record into user_data table [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L218-L230).  Same as movie information data [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L232-L243). For rate data, we do consider a rare situation that a user may re-rate a movie with a different score. So we first check if the “stream_rate_data” table has already had a record for this user rating this movie. If yes, we update the score with new score to avoid duplicated data [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L245-L256). <br>

Beside, we do consider the situation like what if user and movie information API returns invalid result like unvalid JSON format. So we also mock the API behavior to test if the system can handle the unvalided data provided by API [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L149-L197).

The error handling here is to throw “AttributeError” exception with error message to notify the system that the a data input is not valid. We do not try to do correction here since the error pattern is too unpredictable. We simply dump the invalid data to make sure that the system keeps executing correctly without any bad influence. If time permitted, we may try to do data correction and pattern detection to keep more valuable data. <br>

### Feature Extraction

During the phase of feature extraction, we fetch the data from our MongoDB database, get the features we want and generate a csv file. Although we can allow more flexible feature extraction mechanism through allowing users to config what features they want by writing a config.json, we stick to a simpler implementation of extracting `user_id`, `movie_id` and `score`. Here is how we ensure the data quality.

1. Monitoring the validity of `user_id`, `movie_id` and `score`. It is because the pipeline afterwards assume them to be valid numbers (though `user_id` and `movie_id` do not need to be numbers, `score` must be numbers). It is easy to check through checking whether exceptions are being thrown if we try to convert them to numbers. We do this by writing try..except and setting a threshold. If the percentage of invalid data is bigger than the threshold, actions can be taken. For example, the script can generate emails and send them to developers to warn them about potential data schema change or too many missing data.

2. Monitoring the percentage of duplicated data. Exactly same data should not be present in a dataset for machine learning problems. While generating the features, we can calculate the percentage of the duplicated data [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/b58502768c6cb158e02030c81906e324f52e2d9b/feature_extraction/test/test_extract_features.py#L28-L32). Through running this test, we can get a sense of how much duplicated data we have in the database. Further actions include storing a clean deduped version of data back into database to overwrite old data.

### Limitations

Under the current implementations, some issues that might go undetected includes:

1. The same user rate the same movie for many times with different scores. It may be a problem due to the cause of this issue. If it is due to some bug in the front-end of the application, we should fix it. If the user changes his/her mind, we should keep the last record only.

## Test Strategy and Reflection

### Test Strategy:
We have four level tests. 
The first level is **manually test** . When finishing writing program, we manually run the program to test correctness. It's the basic step for achieving program functionality.

The second level is **unit test**. It tests the correctness of each individual module. For example, in the Kafka-Stream-Processing Module, we mock a Kafka stream producer to test whether our system is able to correctly fetch data from remote server. In the Offline Recommend Training Module and Online Prediction Module, we unit test whether the configuration conforms to a particular schema, whether the path we use to open the file exists, whether the some intermediates variables satisfies some constraints, whether each train, evaluate function behaves as expected.

The third level is **integration test**. It tests whether the interaction between two modules are correct or not. The primary interaction form of this project is by intermediate data(mongodb, watch data table, movie data table, feature vector, model). We build scripts to pipeline some procedures and check whether a cascade of two module behaves as expected.

The fourth level is **system level testing**. It tests the correctness of the system as a whole. We conduct this level test by containerize our whole service and deploy it at other place and manually query the API to check whether the system behaves as expected. 

### Test Coverage Report:
![alt text](https://github.com/chenxi1103/17645TeamA/blob/master/README_img/test-coverage-Inference-model.png "test-coverage-Inference-model")
![alt text](https://github.com/chenxi1103/17645TeamA/blob/master/README_img/test-coverage-feature-extraction.png "test-coverage-feature-extraction")
![alt text](https://github.com/chenxi1103/17645TeamA/blob/master/README_img/test-coverage-streamprocess.png "test-coverage-streamprocess")

## Test in Production
### Mechanism
For test in production, we store each client API query result as {“user_Id”: <user_id>, “movies”:[<recommend_movie_id_1>, <recommend_movie_id_2>,…], “query_time”: <query_time>} into a separate table called “query_table_<date>” to record what movies are recommended to a certain user today. We also summary the watch data as {“user_id”: <user_id>, “movie_id”: <movie_id>, “query_time”: <query_time>} into a separate table called “watch_data_<date>” to record what movies are watched by a certain user today. With these two kind of data, we can see if user really watched movies that recommended by our API.

For example, we have the API query records for “2019-10-10”. And we also have the watch data for “2019-10-11”, “2019-10-12”, and “2019-10-13”. Then we can first extract the users that queried our API on “2019-10-10” from query data [[related code]](https://github.com/chenxi1103/17645TeamA/blob/f8bb879bf1e455f7d1d2d1355204ea529672d588/web_server/daily_query_summary.py#L18-L23). And then we can see what movies did these users watch in next three days (“2019-10-11”, “2019-10-12”, and “2019-10-13”) [[related code]](https://github.com/chenxi1103/17645TeamA/blob/f8bb879bf1e455f7d1d2d1355204ea529672d588/web_server/daily_query_summary.py#L52-L62). if they indeed watched the one of the movies we recommended to them, the “counter” will be plused by 1 [[related code]](https://github.com/chenxi1103/17645TeamA/blob/f8bb879bf1e455f7d1d2d1355204ea529672d588/web_server/daily_query_summary.py#L65-L77). And we compute “counter" multipled by the total number of movies we recommended on “2019-10-10” to get the “hit rate” to see if how well our model performs [[related code]](https://github.com/chenxi1103/17645TeamA/blob/f8bb879bf1e455f7d1d2d1355204ea529672d588/web_server/daily_query_summary.py#L34-L41). 

To make our test in production more flexible, the method get_hit_rate(date, delta) in “daily_query_summary.py” takes two input parameters. First one indicates which query date you want to analyze. Second one indicates how many days after the “query date” do you want to collect for the watch data. For example, if we want to see if users watched our recommended movies after three days they queried API on "2019-10-10”, we can simply call get_hit_rate(“2019-10-10", 3)  to get the hit rate. To show the result more clearly, we save the hit rate result into a csv called “[date][_with_delta_][delta].csv’” under "test_in_production/daily_query_summary/“ path. (In this case, the result csv file’s name is “2019-10-10_with_delta_3.csv”)

### Execution Method and Result
To run the test in production mechanism, simply run “python3 daily_query_summary.py [date] [delta]” under “web_server” folder. And then we will get analysis result in "test_in_production/daily_query_summary/[date]_with_delta_[delta].csv”.

The example result is shown as following:

| date       | delta         | hit rate |
|:-------------:|:-------------:| -----:|
| 2019-10-10     | 3 | 0.4 |
| 2019-10-11     | 3 | 0.5 |
| 2019-10-12     | 3 | 0.6 |
| 2019-10-13     | 3 | 0.7 |

If we see a growing trend of hit rate, it indicates that our model has a good performance and earn clients' trusts. If the hit rate keeps going down, we definitely need to reconsider what is going wrong and may be required to retrain the model. 

