import logging
import aiohttp
import discord
import asyncio
from discord.ext import commands
from datetime import datetime as dt

with open('token.txt') as token:
    token = token.readline()

# settings
settings = {
    '0': {
        'id': '431217188410490891',
        'create_channels': 0,
        'default_channel': 'general',
        'watching': ['memes', 'dankmemes', 'curledfeetsies']
    }
}

async def getposts():
    await bot.wait_until_ready()

    for id in settings:
        destination = discord.utils.get(
            bot.get_all_channels(),
            server__id = settings[id]['id'],
            name = settings[id]['default_channel'])
        reddits = list(settings[id]['watching'])
        for reddit in reddits:
            url = f"https://www.reddit.com/r/{reddit}/new/.json"
            posts = []
            now = dt.utcnow()
            images = []
            try:
                with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            json = await resp.json()
                            posts = json['data']['children']
                            posts = list(map(lambda p: p['data'], posts))
                for x in posts:
                    posttime = dt.utcfromtimestamp(x['created_utc'])
                    if (((now - posttime).total_seconds()) / 300) <= 1:
                        # if x['created_utc'] <= int(now) + 14100:
                        images.append(x['url'])

                for image in images:
                    await bot.send_message(destination, image)

            except Exception as e:
                print(e)

    await asyncio.sleep(300)

bot = commands.Bot(command_prefix = '*')

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Type *help for help'))

    # data = {}
    # serverid = bot.guilds.id
    # for server in serverid:
    #     data[server.id] = {
    #         'default_channel': discord.utils.get(bot.get_all_channels(), server__id = server, name = 'general')
    #     }

@bot.command(pass_context = True, name = 'get')
async def getPosts(ctx, reddit, sort):
    pass

if __name__ == '__main__':
    # try:
    #     with open('settings.json', 'a', encoding = 'utf-8') as file
    try:
        bot.loop.create_task(getposts())
        bot.loop.run_until_complete(bot.run(token.strip()))
    except Exception as e:
        print(f'start failed. Exception: {e}')
