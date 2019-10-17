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

For “Kafka streaming” part, it is very important to ensure that the data queried from Kafka topic follows the correct schema. There are two types of ConsumerRecord here. One is watch data which represents the information of a user watch a movie and it follows the schema like:"[TimeStamp],[user_id],GET /data/m/[movie_id]/[block_num].mpg"
The other is rate data which represent the information of how a user rate a movie and it follows the schema like:"[TimeStamp],[user_id],GET /rate/[movie_id]=[score]."<br>

For both watch and rate data, they can be split into 3 pieces by comma. So first we check if this data can be split into exactly 3 piece by comma. [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L45-L52) And we also check if user_id is a numeric string [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L174-L186). Then we check the third piece, which is the most important part. For watch data, it can be split into 5 pieces by “/“ while for rate data it can be split into 3 pieces by “/“. So if the third piece neither can be split into 3 nor 5 pieces, it is invalid [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L66-L91). If the third piece is split into 5 pieces, we should then make sure the second block is exactly “data” [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L66-L91). And if the third piece is split into 3 pieces, we should then make sure the second block is exactly “rate” [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L66-L91). After that, we can extract movie_id out and check if it is not None [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L232-L243). For watch data, we can further extract block_num out. We then check if block_num is a non-negative numeric string[[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L93-L107). For rate data, the movie_id and score can be extracted by splitting last piece by “=“. If splitting result is not two pieces, it is invalid [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L109-L121). Then we further check if score is a numeric string within range 0 to 5 [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L109-L121).  <br>

After extract useful information from Kafka raw streaming data, we also do lots of check before writing them into database. There are four tables in database. One is for user information, one is for movie information, one is for watch data, and one is for rate data. After extract a user_id out, we first check if the user_data table has already had the record for this user. If yes, we do nothing. If no, we query the API and insert a new record into user_data table [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L218-L230).  Same as movie information data [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L232-L243). For rate data, we do consider a rare situation that a user may re-rate a movie with a different score. So we first check if the “stream_rate_data” table has already had a record for this user rating this movie. If yes, we update the score with new score to avoid duplicated data [[related test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L245-L256). <br>

Beside, we do consider the situation like what if user and movie information API returns invalid result like unvalid JSON format. So we also mock the API behavior to test if the system can handle the unvalided data provided by API [[related_test]](https://github.com/chenxi1103/17645TeamA/blob/ee3dd5b94986afa9253a16074edcae3352a919b7/kafka_mongodb_process/test.py#L149-L197).

The error handling here is to throw “AttributeError” exception with error message to notify the system that the a data input is not valid. We do not try to do correction here since the error pattern is too unpredictable. We simply dump the invalid data to make sure that the system keeps executing correctly without any bad influence. If time permitted, we may try to do data correction and pattern detection to keep more valuable data. <br>
