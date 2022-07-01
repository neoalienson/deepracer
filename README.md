* Info
Right Steering -30
Left Steering 30
Max Speed 4
SIM_TRACE_LOG: episode, step, x-coordinate, y-coordinate, heading, steering_angle, 
  speed, action_taken, reward, job_completed, all_wheels_on_track, progress,
  closest_waypoint_index, track_length, time.time()

* Using loganalysis

# aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 sync s3://bucket/rl-deepracer-sagemaker data/logs/download
# Training_analysis to model_logs_root = '/workspace/logs/download' 
** Using Action space anaylsis
# Download https://github.com/dgnzlz/Capstone_AWS_DeepRacer/tree/master/Compute_Speed_And_Actions https://raw.githubusercontent.com/dgnzlz/Capstone_AWS_DeepRacer/master/Compute_Speed_And_Actions/RaceLine_Speed_ActionSpace.ipynb
# Download raceline https://github.com/cdthompson/deepracer-k1999-race-lines/blob/master/racelines/reinvent_base-400-4-2019-10-11-161903.npy
# update fpath = "/workspace/analysis/reinvet_base-400-4-2019-10-11-161903.npy"
# race line https://github.com/cdthompson/deepracer-k1999-race-lines/blob/master/racelines/reinvent_base-400-4-2019-10-11-161903.py