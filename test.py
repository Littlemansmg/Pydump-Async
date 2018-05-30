import json
import aiohttp
import discord
import asyncio
from collections import defaultdict

with open('options.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

url = "https://www.reddit.com/r/redheads/new/.json"

posts = []
async def test():
    # Try to open connection to reddit with async
    with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:  # 200 == good
                json = await resp.json()
                posts = json['data']['children']
                # puts each post into a dict that can be manipulated
                posts = list(map(lambda p: p['data'], posts))
    return posts

async def test2():

    posts = await test()

    for x in posts:
        if x["over_18"] == True:
            print(x["over_18"])

loop = asyncio.get_event_loop()
loop.run_until_complete(test2())