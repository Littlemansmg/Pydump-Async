# import aiohttp
# import asyncio
# from datetime import datetime as dt
#
# reddit = input('Name of subreddit. Ex. r/dankmemes: ')
# sort = input('Sorted by? New/Top/Hot: ')
#
# async def getpost():
#     url = f'https://www.reddit.com/r/{reddit}/{sort.strip()}/.json'
#     posts = []
#     now = dt.utcnow()
#     images = []
#     try:
#         with aiohttp.ClientSession() as session:
#             async with session.get(url) as resp:
#                 if resp.status == 200:
#                     json = await resp.json()
#                     posts = json['data']['children']
#                     posts = list(map(lambda p: p['data'], posts))
#         for x in posts:
#             posttime = dt.utcfromtimestamp(x['created_utc'])
#             if (((now - posttime).total_seconds()) / 300) <= 1:
#             #if x['created_utc'] <= int(now) + 14100:
#                 images.append(x['url'])
#             else:
#                 return images
#     except Exception as e:
#         print(e)
#     finally:
#         return images
#
# async def display():
#     images = await getpost()
#     print(images)
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(display())

def test():
    return [123]

if not test():
    print("false")
elif test():
    print("true")