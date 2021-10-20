#!/bin/bash

IMAGE=$1
CAM=$2

# Create a temp folder
TMP_DIR=`mktemp -d`
trap "rm -rf $TMP_DIR" EXIT
echo TMP_DIR $TMP_DIR

# Extract micro python from SDK image
ID=`docker create $IMAGE`
docker cp $ID:/src/micropython/ports/unix/micropython $TMP_DIR
docker cp $ID:/target-libs $TMP_DIR/libs
docker cp $ID:/usr/lib/micropython $TMP_DIR/micropython-libs
docker rm $ID

# Upload to camera
scp -r $TMP_DIR/* $CAM:/tmp
