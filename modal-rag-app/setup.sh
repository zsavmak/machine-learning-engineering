#!/bin/bash

# This command is idempotent. It creates the volume only if it doesn't exist.
modal volume create model-cache-volume
modal volume create source-volume
modal volume create vector-store-volume

echo "Volumes 'source-volume', 'vector-store-volume', and 'model-cache-volume' are ready."
