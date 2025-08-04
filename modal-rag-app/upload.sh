#!/bin/bash
DB_NAME=$1
LOCAL_PATH=$2

if [ -z "$DB_NAME" ] || [ -z "$LOCAL_PATH" ]; then
  echo "Usage: ./upload.sh <database_name> <local_directory_path>"
  exit 1
fi

# This prevents Git Bash from changing the remote path.
export MSYS_NO_PATHCONV=1

# Upload to the root of the volume, not a /data subdirectory.
modal volume put source-volume "$LOCAL_PATH" "/$DB_NAME"
