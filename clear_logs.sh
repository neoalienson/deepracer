#!/bin/bash
rm ../data/logs/training-simtrace/*.csv
rm ../data/logs/training-simtrace/*.dsv
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 sync --recursive s3://bucket/rl-deepracer-*
