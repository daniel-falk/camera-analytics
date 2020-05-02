#!/bin/bash

IMAGE=$1
CAM=$2

# Create a temp folder
TMP_DIR=`mktemp -d`
trap "rm -rf $TMP_DIR" EXIT
echo RMP_DIR $TMP_DIR

# Extract micro python from SDK image
ID=`docker create $IMAGE`
docker cp $ID:/src/micropython/ports/unix/micropython $TMP_DIR
docker rm $ID

# Upload to camera
scp $TMP_DIR/micropython $CAM:/tmp
