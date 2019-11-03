#!/usr/bin/env bash

python3 feature_extraction/extract_features.py
mv feature_extraction/data/usermovie.csv inference/feature/
sh train_evaluate.sh