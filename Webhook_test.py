import logging
# import aiohttp
import discord
from discord.ext import commands
import urllib.request, json

with open('token.txt') as token:
    token = token.readline()

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

    await bot.say("complete!")

bot.run(token.strip())
