#
# Extract distinct sites from urls
#

from urllib.parse import urlparse
import csv, re, sys


def extract_sites(filename):
    with open(filename, newline='') as csvfile:
        for row in csv.DictReader(csvfile):
            url = row['url']
            if 'reddit.com/r/' in url:
                matches = re.match('(https?:\/\/(www.)?reddit.com\/r\/\w+)\/?', url)
                yield matches[0]
            else:
                hostname = urlparse(url).hostname
                domains = hostname.split('.')
                # Remove www because that is equivalent to bare site name
                if domains[0] == 'www':
                    del domains[0]
                yield '.'.join(domains)


input = sys.argv[1]
print(set(extract_sites(input)))
