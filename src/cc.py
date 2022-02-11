from comcrawl import IndexClient

url = 'http://gabrielecirulli.github.io/2048/'

client = IndexClient()
client.search(url)
first_hit = filter(lambda r: r['status'] == '200', client.results).__next__()
client.results = [first_hit]
client.download()
