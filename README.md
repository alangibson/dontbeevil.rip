
# TODO

- Enable ES Xpack security
  - Change ES self-signed cert to ACM cert
  - Update API GW to make authenticated calls
- Point dontbeevil.rip to https://xo46sg6aeg.execute-api.us-east-1.amazonaws.com/prod
  - Register dontbeevil.rip

# Usage

```
sudo apt update; apt install python3 python3-pip awscli
aws configure
pip install -r requirements.txt
curl -L -O https://joieride-search.s3.amazonaws.com/crawled_urls/2022/02/10/c2c0610a-cc4f-488b-86e3-3b4d16dd465c.csv
python3 src/urls-to-s3-requests.py *.csv ./warcs ./dl > /dev/null
./run-dl.sh > run-dl.log &
python3 src/warc-to-bulk.py ./warcs ./ndjson 1000 0 > warc-to-bulk.log &
# watch "./status.sh"
./src/upload-to-elasticsearch.sh \
  https://ec2-3-238-77-187.compute-1.amazonaws.com:9200/main \
  "$ES_PASSWORD"
```

# Datasets

## HackerNews

Analyzing Hacker News Dataset
  https://victoromondi1997.github.io/blog/data-analysis/hacker-news/2020/08/30/Analyzing-Hacker-News-Dataset.html

Hacker News Stories and comments since 2006
  https://console.cloud.google.com/marketplace/product/y-combinator/hacker-news

Hacker News on BigQuery: Now with daily updates — So what are the top domains?
  https://hoffa.medium.com/hacker-news-on-bigquery-now-with-daily-updates-so-what-are-the-top-domains-963d3c68b2e2

Full dataset:
  bigquery: bigquery-public-data:hacker_news.stories
  schema:
    id: string
    url: string
    score: integer
    time: integer
    author: string
    deleted: boolean
  
## StackOverflow

Full dataset:

  bigquery:  bigquery-public-data:stackoverflow.comments 
    schema:
      id: integer
      text: string
      score: integer 
      user_id: integer
      creation_date: string
  rows: 83,160,601 
  
  bigquery: bigquery-public-data:stackoverflow.users 
    schema:
      id: integer
      creation_date: string
      last_access_date: string
      reputation: integer
      up_votes: integer
      down_votes: integer
      views: integer
    rows: 16,279,655 

## CommonCrawl

So you’re ready to get started
  https://commoncrawl.org/the-data/get-started/

Registry of Open Data on AWS : Common Crawl
  https://registry.opendata.aws/commoncrawl/

Index to WARC Files and URLs in Columnar Format (AWS Athena)
  https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/

Common Crawl Index Server (index search and downloadable indexes)
  https://index.commoncrawl.org/

Columnar Parquet index:
  s3://commoncrawl/cc-index/table/cc-main/warc/

Full dataset:
  arn:    arn:aws:s3:::commoncrawl
  region: us-east-1
  cli:    aws s3 ls --no-sign-request s3://commoncrawl/

## HTTP Archive

Full dataset:
  bigquery: httparchive:pages.2022_01_01_desktop
  rows: 5,776,631
  schema:
    url: string

## Reddit

Full dataset:
  bigquery: fh-bigquery:reddit_posts.2019_08 
  schema:
    id: string
    selftext: string
    url: string 
    score: integer
    created_utc: integer
    subreddit: string
    distinguished: string
    num_comments: integer
    author: string
    quarantine: boolean
  rows: 21,927,461 

# Pricing

## S3

https://aws.amazon.com/s3/pricing/

You pay for all bandwidth into and out of Amazon S3, except for the following:
- Data transferred out to the internet for the first 100GB per month, aggregated across all AWS Services and Regions (except China and GovCloud)
- Data transferred between S3 buckets in the same AWS Region. 
- Data transferred from an Amazon S3 bucket to any AWS service(s) within the same AWS Region as the S3 bucket (including to a different account in the same AWS Region).

Data Transfer IN To Amazon S3 From Internet: $0.00 per GB
Data Transfer OUT From Amazon S3 To Internet: $0.09 per GB

## BigQuery

https://cloud.google.com/bigquery/pricing

Active storage: $0.020 per GB.	The first 10 GB is free each month.
Queries (on-demand):	$5.00 per TB	The first 1 TB per month is free.

## BigQuery Omni

https://cloud.google.com/bigquery/pricing#bqomni

## BigQuery public datasets 

https://cloud.google.com/bigquery/public-data

Queries processing 1 TB / month free
No storage fee

## AWS Athena

https://aws.amazon.com/athena/pricing/

5.00 USD per TB of data scanned
You are charged for the number of bytes scanned by Amazon Athena, rounded up to the nearest megabyte, with a 10MB minimum per query. 
Cancelled queries are charged based on the amount of data scanned.
Compressing your data allows Athena to scan less data. Converting your data to columnar formats allows Athena to selectively read only required columns to process the data. Athena supports Apache Parquet. Partitioning your data also allows Athena to restrict the amount of data scanned.
Amazon Athena queries data directly from Amazon S3. There are no additional storage charges for querying your data with Athena. You are charged standard S3 rates for storage, requests, and data transfer. By default, query results are stored in an S3 bucket of your choice and are also billed at standard Amazon S3 rates.

## BigQuery Data Transfer Service

https://cloud.google.com/bigquery-transfer/docs/s3-transfer

To S3, No charge. BigQuery Quotas and limits apply.
https://cloud.google.com/bigquery/quotas#export_jobs

# Analysis

## Prepare data set

- Extract urls and scores from HN dataset on BigQuery
- Download and transform to compressed Parquet file using `bq` cli
  - Exporting data from Google BigQuery into AWS Athena
    https://big-data-demystified.ninja/2018/05/27/how-to-export-data-from-google-big-query-into-aws-s3-emr-hive/
- Upload compressed Parquet file of HN urls and scores to S3 with `aws` cli
- Join HN urls to CC text and linked urls in AWS Athena
- Save results to compressed Parquet file in S3 bucket
- Download from S3 bucket

# Algorithm

## Discover

### Seed

- Load urls from HackerNews public archive export
- Send messages into queueing system

- Load urls form Reddit (https://files.pushshift.io/reddit/)
- Send messages into queueing system

### Scheduled

- Gather urls from Reddit and HackerNews
- Order by most upvoted
- Send messages into queueing system

## Crawl queue

- Get discover message from queueing system
- Deduplicate by url
- Don't crawl if recently crawled
- Request url
  - If not found, put in error queue
- Store in cache
- Send message to index queue

## Crawl error queue

- Get message from error queue
- Look up url in CommonCrawl search
- Download page
  - If not found, throw away message and loop
- Store in cache
- Send message to index queue

## Index

- Get url content from cache
- Extract urls from text
- Enqueue urls in crawl queue
- Extract main body text
- Preprocess text
- Store to index

# Commands

## Get CC WARC record

To get a single WARC record

bucket = commoncrawl
key = ccindex.warc_filename
start of byte range = ccindex.warc_record_offset
end of byte range = ccindex.warc_record_offset + (ccindex.warc_record_length - 1)
```
aws s3api get-object --range 'bytes=30680420-30681660' --bucket 'commoncrawl' --key 'crawl-data/CC-MAIN-2022-05/segments/1642320301217.83/warc/CC-MAIN-20220119003144-20220119033144-00465.warc.gz' out.gz
```

# Research

## Relevance

Just run query expression?

Natural language processing:
- https://www.nltk.org/

## Boosting

- Rating of url on community site
- PageRank of site

## PageRank

Pagerank juice applies to sites only

- https://anvil.works/blog/search-engine-pagerank

## Siteness

"public suffix"+1 is a site (https://publicsuffix.org/list/public_suffix_list.dat)

    Given public suffix co.uk, theregister.co.uk is a site

eTLD+1 is equivalent to www.(eTLD+1)

    reddit.com == www.reddit.com

Siteness does not extend to subdomains

    medium.com != marker.medium.com

or paths

    www.reddit.com != www.reddit.com/r/identifythisfont

