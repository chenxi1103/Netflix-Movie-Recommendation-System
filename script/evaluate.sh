#!/usr/bin/env bash
ROOT_PATH="/Users/yangzhouyi/Desktop/17645/Assignment/HW6G3/17645TeamA/"
SCRIPT_PATH="/inference/RecommendModule/evaluate.py"
CONFIG_PATH="/inference/configuration/offline_config.json"
EXPERIMENT_NAME="exp-1"
python $ROOT_PATH$SCRIPT_PATH $ROOT_PATH $ROOT_PATH$CONFIG_PATH $EXPERIMENT_NAME
