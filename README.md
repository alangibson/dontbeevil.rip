# DontBeEvil.rip : Search, for Programmers

DontBeEvil.rip is a year long experiment to see if a small team can build a developer-focused search engine that is self-sustaining on $10 monthly subscriptions.

If the service isn't self-sustaining by March 1st 2023, it will be shut down. If it is, then it will be scaled up in these wonderful ways:

- Allow affinity groups to manage their own site lists
- Expand scope of indexed resources to all STEM subjects
- Run our own crawler on the most active sites
- Add a Way Back Machine style cache

## Caveats

I believe that, when you consume a service, if you aren't paying then you're being sold. I don't want to ever be in a position to have to sell my user base. In the interest of openness and transparency, I want to be clear that I intend to start charging for this service as soon as I think it is worth $10 per month. My tentative plan is to implement subscriptions in early Q2 2022.

DontBeEvil.rip is aggressively alpha at this point. Don't use it for anything critical. It _will_ disappear from time to time.

## Status

HackerNews, StackOverflow, Arxiv abstracts, 2M Github repos, and Programmer Reddit (up to 2020) are being indexed. 

The limited, but awesome, features in this first release are:

- Expressions! Experience the power of Elasticsearch's [Simple Query Strings](https://www.  elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html)
- REST API

Next priorities are:

- Fresher Reddit posts
- More Github repos
- Index sites on the open web (starting March 2022)
- Pagination
- Simple web UI
- Start charging

## Usage

### Prerequisites

```bash
apt install curl jq
pip3 install jtbl
```

### Searching with the CLI

```
curl -O https://github.com/alangibson/dontbeevil/src/rip && chmod u+x rip
./rip 'what is a monad'
```

### Requesting from API

Just take a look at the CLI script. It's pretty self explanatory.

```bash
cat rip
```

## Suggestions

<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSeRtGev6GruCISC5n_e-39VNzJJkKjULLY0UJSFnbntAum5Hw/viewform?embedded=true" width="640" height="724" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe>