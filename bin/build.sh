#! /bin/bash
# Build a docker image
cd ..
docker build -t pyengine/aws-cloudtrail .
docker tag pyengine/aws-cloudtrail pyengine/aws-cloudtrail:1.0
docker tag pyengine/aws-cloudtrail spaceone/aws-cloudtrail:1.0
