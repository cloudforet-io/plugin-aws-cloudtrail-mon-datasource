#!/usr/bin/env bash
# How to upload
./build.sh
docker push pyengine/aws-cloudtrail:1.0
docker push spaceone/aws-cloudtrail:1.0
