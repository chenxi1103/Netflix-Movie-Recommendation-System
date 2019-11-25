#!/usr/bin/env bash

python3 feature_extraction/extract_features.py
mv feature_extraction/data/usermovie.csv inference/feature/
echo "Feature Extraction Succeeded"

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

echo '#!/usr/bin/env bash' > workflow/run_server.sh
echo '2to3 -w /usr/local/lib/python3.7/site-packages/pyflann' >> workflow/run_server.sh
command_str='python3 web_server.py ../ '${DailyActiveModelSetting}  
echo $command_str >> workflow/run_server.sh
mv workflow/run_server.sh web_server/run_server.sh

current=`date "+%Y-%m-%d %H:%M:%S"`
timeStamp=`date -d "$current" +%s`
image_name=${DailyActiveModelSetting}'-'${timeStamp}

echo 'Building container:'$image_name
sudo docker build -t web-service:$image_name .
imageId=`sudo docker images -q teama/web-service:${image_name}`
echo 'Build docker image successfully, imageId is: '$imageId

python3 workflow/send_new_release_to_supervisor.py 'Canary' 'teama/web-service:'${image_name}

python3 workflow/check_model_status.py
if [ $? -eq 0 ]
then
   echo 'Canary Test Succeeded! Model is Ready to Release!'
else
   echo 'Canary Test Failed! Model is going to rollback!'
   exit 1 
fi
