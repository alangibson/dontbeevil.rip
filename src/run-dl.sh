#!/bin/bash

set -e

SOURCE_DIR="./dl"

for filename in $SOURCE_DIR/*.sh; do
    echo "Running $filename";
    source "$filename";
    rm -f "$filename";
done