# Track 
DR_ENABLE_DOMAIN_RANDOMIZATION is set to true to simulate real environment

# Model Parameter
Right Steering -30
Left Steering 30
Max Speed 4

# Using loganalysis
* x jupyter-lab --no-browser
* x Open https://github.com/aws-deepracer-community/deepracer-analysis
* aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 sync s3://bucket/rl-deepracer-sagemaker data/logs/download
* dr-log-analysis
* Training_analysis to model_logs_root = '/workspace/logs/download' 

## Using Action space anaylsis
* Download https://github.com/dgnzlz/Capstone_AWS_DeepRacer/tree/master/Compute_Speed_And_Actions https://raw.githubusercontent.com/dgnzlz/Capstone_AWS_DeepRacer/master/Compute_Speed_And_Actions/RaceLine_Speed_ActionSpace.ipynb
* Download raceline https://github.com/cdthompson/deepracer-k1999-race-lines/blob/master/racelines/reinvent_base-400-4-2019-10-11-161903.npy
* update fpath = "/workspace/analysis/reinvet_base-400-4-2019-10-11-161903.npy"
* race line https://github.com/cdthompson/deepracer-k1999-race-lines/blob/master/racelines/reinvent_base-400-4-2019-10-11-161903.py

# AWS commands
* aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 ls s3://bucket
* aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 rm --recursive s3://bucket/rl-deepracer-1

# References
* https://blog.gofynd.com/how-we-broke-into-the-top-1-of-the-aws-deepracer-virtual-circuit-573ba46c275
* https://medium.com/axel-springer-tech/how-to-win-aws-deepracer-ce15454f594a


aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 ls s3://bucket/
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 cp s3://bucket/rl-deepracer-3/mp4/camera-pip/0-video.mp4 .
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 --recursive rm s3://bucket/rl-deepracer-1/
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 cp s3://bucket/rl-deepracer-sagemaker/mp4/camera-topview/0-video.mp4 . 
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 cp s3://bucket/rl-deepracer-sagemaker/evaluation-20221007222447/evaluation-simtrace/0-iteration.csv

docker swarm leave --force
bin/init.sh -a cpu
source bin/activate.sh
cd custom_files
git restore README.md hyperparameters.json model_metadata.json reward_function.py
cp run.env ..

git add . && git commit -m update && git tag -d 202210090200 && git tag -a 202210090200 -m ""
dr-upload-custom-files  && dr-start-training -w