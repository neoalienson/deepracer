#!/bin/bash
rm ../data/logs/training-simtrace/*.csv

pushd ../data/logs/training-simtrace
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 sync s3://bucket/rl-deepracer-sagemaker/training-simtrace/  .
find . -name "*.csv" -exec sh -c 'f="{}"; mv -- "$f" "${f%.csv}.dsv"' \;
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 sync s3://bucket/rl-deepracer-1/training-simtrace/  .
find . -name "*.csv" -exec sh -c 'f="{}"; mv -- "$f" "${f%.csv}.esv"' \;
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 sync s3://bucket/rl-deepracer-2/training-simtrace/  .
find . -name "*.csv" -exec sh -c 'f="{}"; mv -- "$f" "${f%.csv}.fsv"' \;
aws $DR_LOCAL_PROFILE_ENDPOINT_URL s3 sync s3://bucket/rl-deepracer-3/training-simtrace/  .
find . -name "*.csv" -exec sh -c 'f="{}"; mv -- "$f" "${f%.csv}.fsv"' \;

ls -vrt | cat -n | while read n f; do mv -n "$f" "$n-iteration.csv"; done 

ls -rlt
popd
