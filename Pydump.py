import time
import urllib.request, json

url = 'https://www.reddit.com/r/dankmemes/new/.json'

with urllib.request.urlopen(url) as post:
    data = json.loads(post)['data']['children']['data']

print (data)
