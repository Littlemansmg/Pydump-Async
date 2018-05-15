import time
import urllib.request, json

reddit = input('Name of subreddit. Ex. r/dankmemes: ')
sort = input('Sorted by? New/Top/Hot: ')

url = f'https://www.reddit.com/r/{reddit}/{sort.strip()}/.json'

try:
    with urllib.request.urlopen(url) as post:
        data = json.loads(post.read().decode())
    print(data['data']['children'][0]['data']['url'])

except:
    print('Sorry, can\'t get to that reddit or it doesn\'t exist.')

