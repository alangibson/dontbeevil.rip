#!/bin/bash

#
# Download exported resources from BigQuery and transform into 
# Elasticsearch bulk load resources
#

set -e

START="${1-0}"
END="$2"
BUCKET_NAME="${3-joieride-search}"
TABLE_NAME="${4-combined_posts}"

for i in $(seq $START $END); do 
    # Figure out filename
    counter=`printf %012d $i`
    filename="${TABLE_NAME}-${counter}.csv.gz"

    # Download data
    url="https://storage.googleapis.com/${BUCKET_NAME}/${filename}"; 
    echo "Downloading $url"
    curl -L -O "$url"

    # TODO Process filename into ES builk queries in ./ndjson

    # TODO Delete filename
    # rm -f "$filename"

done
