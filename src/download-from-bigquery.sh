#!/bin/bash

#
# Download exported resources from BigQuery and transform into 
# Elasticsearch bulk load resources
#

set -e

END="$1"
START="${2:-0}"
OUTDIR="${3:-./bq}"
BUCKET_NAME="${4:-joieride-search}"
TABLE_NAME="${5:-combined_posts/combined_posts}"

mkdir -p "$OUTDIR"
pushd "$OUTDIR"

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

popd
