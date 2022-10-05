#!/bin/bash
rm ../data/logs/training-simtrace/*.csv
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 rm --recursive s3://bucket/rl-deepracer-*
