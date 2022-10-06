#!/bin/bash
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 rm --recursive s3://bucket/rl-deepracer-1
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 ls s3://bucket
rm ../data/logs/training-simtrace/*.csv