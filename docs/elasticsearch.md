
```
ssh -i ~/Documents/oxcart.pem ubuntu@ec2-3-238-77-187.compute-1.amazonaws.com

wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.0.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.0.0-linux-x86_64.tar.gz
cd elasticsearch-8.0.0/
export ES_HOME="$PWD"

# Initial setup
./bin/elasticsearch
```

### Install as systemd service

https://www.elastic.co/guide/en/elasticsearch/reference/current/starting-elasticsearch.html#start-deb

### Run as daemon

```
# Start
./bin/elasticsearch -d -p pid

# Stop
pkill -F pid
```

### Ping

```
# Local
curl --cacert $ES_HOME/config/certs/http_ca.crt -u "elastic:$ES_PASSWORD" https://localhost:9200 

# Remote
curl -k -u "elastic:$ES_PASSWORD" https://ec2-3-238-77-187.compute-1.amazonaws.com:9200
```

### Bulk load

```
curl -k -u "elastic:$ES_PASSWORD" -H "Content-Type: application/x-ndjson" -XPOST \
https://ec2-3-238-77-187.compute-1.amazonaws.com:9200/main/_bulk \
--data-binary "@jsonl/1.jsonl" | jq .errors
```

### Search

```
curl -k -u "elastic:$ES_PASSWORD" -X GET -H 'Content-Type: application/json' \
https://ec2-3-238-77-187.compute-1.amazonaws.com:9200/main/_search?pretty -d'
{
  "query": {
    "simple_query_string" : {
        "query": "apple maps",
        "default_operator": "and"
    }
  }
}'
```

### Reset password

```
bin/elasticsearch-reset-password -u elastic
```

### Add nodes to cluster

ℹ️  Configure other nodes to join this cluster:
• On this node:
  ⁃ Create an enrollment token with `bin/elasticsearch-create-enrollment-token -s node`.
  ⁃ Uncomment the transport.host setting at the end of config/elasticsearch.yml.
  ⁃ Restart Elasticsearch.
• On other nodes:
  ⁃ Start Elasticsearch with `bin/elasticsearch --enrollment-token <token>`, using the enrollment token that you generated.




eyJ2ZXIiOiI4LjAuMCIsImFkciI6WyIxNzIuMzEuNjUuMjAzOjkyMDAiXSwiZmdyIjoiMjdjOTc3NDMyYTE3YTkzNGUxMDVkZjlhNjFkN2MyODU0YjI5OTJiNmNiOTNhNjcwYjExZTZhNDU0OGViZjQzYiIsImtleSI6Ii0tb2I4bjRCWDlDai1RN2xyWXRnOmJTbEpRV002VF9tUHdlRHJGdGNUemcifQ==
