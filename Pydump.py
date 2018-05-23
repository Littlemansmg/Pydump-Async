"""

"""

# ---------------------------Imports---------------------------------
import logging
import aiohttp
import discord
import asyncio
import json
from discord.ext import commands
from datetime import datetime as dt

# ---------------------------Logs------------------------------------

def commandinfo(ctx):
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Command Used; '
                 f'Server_id: {ctx.message.server.name} '
                 f'Author_id: {str(ctx.author.id)} '
                 f'Invoke: {ctx.message.content}')

def taskcomplete():
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Task completed successfully!')

def catchlog(exception):
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Exception Caught: {exception}')

# ---------------------------Tasks-----------------------------------
async def getposts():
    """
    This function is the task that gets reddit posts on a 5 minute timer.
    """
    await bot.wait_until_ready()

    while True:
        now = dt.utcnow()
        for id in data:
            # get default destination from json file
            destination = discord.utils.get(
                bot.get_all_channels(),
                server__id = data[id]['id'],
                name = data[id]['default_channel']
            )

            # if not destination:
            #     # bot.get_guild(
            #     Server = bot.get_guild(settings[id]['id'])
            #     await bot.send_message(Server, "I don't have a default channel to post in!"
            #                                                     "please type `*default_channel` to set it!")
            #     break
            # reddits that the server is watching
            reddits = list(data[id]['watching'])
            # if not reddits:
            #     await bot.send_message(destination, "I don't have any reddit's to watch! Please type `*subscribe "
            #                                         "<reddit names>` to start watching so I can post!")
            #     break

            for reddit in reddits:
                posts = []
                images = []
                url = f"https://www.reddit.com/r/{reddit}/new/.json"

                try:
                    # Try to open connection to reddit with async
                    with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            if resp.status == 200: # 200 == good
                                json = await resp.json()
                                posts = json['data']['children']
                                # puts each post into a dict that can be manipulated
                                posts = list(map(lambda p: p['data'], posts))

                except Exception as e:
                    catchlog(e)
                    continue

                for x in posts:
                    posttime = dt.utcfromtimestamp(x['created_utc'])
                    # if 300 can't go into total seconds difference once, it gets added to the list of urls
                    if (((now - posttime).total_seconds()) / 300) <= 1:
                        images.append(x['url'])

                    if not images:
                        await asyncio.sleep(1)
                        break

                for image in images:
                    await bot.send_message(destination, f'From r/{reddit} ' + image)
                    await asyncio.sleep(1) # sleep for 1 second to help prevent the ratelimit from being reached.

        taskcomplete()
        await asyncio.sleep(300) # sleep for 5 minutes before it repeats the process

# ---------------------------Bot-------------------------------------
bot = commands.Bot(command_prefix = '*')

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Type *help for help'))

@bot.command(pass_context = True, name = 'get')
async def getPosts(ctx, reddit, sort):
    pass

@bot.group(pass_context = True, name = 'default')
async def setDefaults(ctx):
    if ctx.invoked_subcommand is None:
        bot.say('No subcommands invoked.')
        commandinfo(ctx)

@setDefaults.command(pass_context = True, name = 'channel')
async def defaultChannel(ctx, channel):
    newchannel = discord.utils.get(bot.get_all_channels(), name = channel)
    await bot.say(f'Is {newchannel.name} correct?')

    commandinfo(ctx)

# ---------------------------Run-------------------------------------
if __name__ == '__main__':
    # get token
    with open('token.txt') as token:
        token = token.readline()

    # Start Logging
    logging.basicConfig(handlers=[logging.FileHandler('discord.log', 'a', 'utf-8')],
                        level=logging.INFO)

    # get .json file
    with open('options.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # run bot/start loop
    try:
        bot.loop.create_task(getposts())
        bot.loop.run_until_complete(bot.run(token.strip()))
    except Exception as e:
        catchlog(e)
