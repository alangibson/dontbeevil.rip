#!/bin/bash -e

for filename in ./dl/*.sh; do
    echo "Running $filename";
    source "$filename";
    rm -f "$filename";
done