nohup python3 kafak_stream_process.py &
nohup python3 feedback_detection_batch.py &
ssh -L 9092:localhost:9092 tunnel@128.2.204.215 -NT
