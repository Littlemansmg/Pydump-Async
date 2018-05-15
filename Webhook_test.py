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
    bot.change_presence(game=discord.Game(name='Type *help for help'))

@bot.command(pass_context = True, name = 'get')
async def getPosts(ctx, reddit, sort):

    url = f'https://www.reddit.com/r/{reddit}/{sort}/.json'

    try:
        with urllib.request.urlopen(url) as post:
            data = json.loads(post.read().decode())
        bot.say(data['data']['children'][0]['data']['url'])

    except:
        bot.say('Sorry, can\'t get to that reddit or it doesn\'t exist.')

bot.run(token.strip())
