#!/usr/bin/env bash

#python3 feature_extraction/extract_features.py
#mv feature_extraction/data/usermovie.csv inference/feature/
#echo "Feature Extraction Succeeded"

. ./workflow/active_model_setting_config.sh
echo "Chosen ModelSetting:""${DailyActiveModelSetting}"

python3 inference/RecommendModule/operate.py . ${DailyActiveModelSetting}  Train
if [ $? -eq 0 ]
then
   echo 'Training succeeded'
else
   echo 'Training Failed'
   exit 1 
fi

python3 inference/RecommendModule/operate.py . ${DailyActiveModelSetting} Evaluation
if [ $? -eq 0 ]
then
   echo 'Evaluation succeeded'
else
   exit 1 
fi


