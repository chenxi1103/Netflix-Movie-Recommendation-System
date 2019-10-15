#!/usr/bin/env bash
ROOT_PATH="/home/teama/17645TeamA/"
SCRIPT_PATH="/inference/RecommendModule/evaluate.py"
CONFIG_PATH="/inference/configuration/offline_config.json"
EXPERIMENT_NAME="exp-1"
python3 $ROOT_PATH$SCRIPT_PATH $ROOT_PATH $ROOT_PATH$CONFIG_PATH $EXPERIMENT_NAME
