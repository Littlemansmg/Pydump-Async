import json
from collections import defaultdict

with open('options.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

subs = data['0']['watching']
subs.append('atbge')
data['0']['watching'] = subs

print(data['0']['watching'])