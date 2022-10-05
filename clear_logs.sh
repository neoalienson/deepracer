#!/bin/bash
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 rm --recursive s3://bucket/rl-deepracer-1
rm ../data/logs/training-simtrace/*.csv