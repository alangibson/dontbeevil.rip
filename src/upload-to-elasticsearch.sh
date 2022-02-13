#!/bin/bash

set -e

INDEX_URL="$1"
ES_PASSWORD="$2"
SOURCE_DIR="${3:-ndjson}"
ES_USERNAME="${4:-elastic}"

for filename in $SOURCE_DIR/*.ndjson; do
    echo "Uploading $filename";
    ERRORS=$(curl -s -k -u "$ES_USERNAME:$ES_PASSWORD" \
        -H "Content-Type: application/x-ndjson" \
        -X POST "$INDEX_URL/_bulk" \
        --data-binary "@${filename}" | jq .errors);
    echo "Where errors encountered processing $filename: $ERRORS"
    if [ $ERRORS == "true" ]; then
        echo "Exiting due to previous error"
        exit 1;
    else
        rm -f $filename;
    fi
done

echo "Done uploading. Exiting."
exit 0;