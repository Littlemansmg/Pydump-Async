import logging
# import aiohttp
import discord
import asyncio
from discord.ext import commands
import urllib.request, json

with open('token.txt') as token:
    token = token.readline()

async def getposts():
    pass

bot = commands.Bot(command_prefix = '*')

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Type *help for help'))

@bot.command(pass_context = True, name = 'get')
async def getPosts(ctx, reddit, sort):
    destination = ctx.message.channel
    url = f'https://www.reddit.com/r/{reddit}/{sort}/.json'

    try:
        with urllib.request.urlopen(url) as post:
            data = json.loads(post.read().decode())
        img = data['data']['children'][0]['data']['url']
        await bot.say(img)
    except:
        await bot.say('Sorry, can\'t get to that reddit or it doesn\'t exist.')

if __name__ == '__main__':
    try:
        bot.loop.create_task(getposts())
        bot.loop.run_until_complete(bot.run(token.strip()))
    except Exception as e:
        print(f'start failed. Exception: {e}')
