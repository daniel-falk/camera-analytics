TARGET_DIR=$1
MODULE_DIR=$2
MODULE_NAME=$3

HEADER_FILE=./mpconfigport.h

# Script is assumed to be run from directory with port config file in
test -f $HEADER_FILE

# Create target dir if not already there
mkdir -p $TARGET_DIR

# Link the module code to the target dir
ln -s $MODULE_DIR $TARGET_DIR/$MODULE_NAME

# Enable module in header file
ENABLE_DEFINE=MODULE_${MODULE_NAME}_ENABLED
cat <<EOT >> $HEADER_FILE
#ifndef $ENABLE_DEFINE
#define $ENABLE_DEFINE (1)
#endif
EOT
