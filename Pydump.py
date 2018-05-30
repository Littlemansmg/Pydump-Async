"""
Pydump-Rewrite by Scott 'LittlemanSMG' Goes on 5/24/18 (not actual date, just the date I decided to make this part.
Pydump is a bot that is used to send reddit posts to discord per server.

Using Discord.py
github www.github.com/littlemansmg/Pydump-rewrite
"""

# ---------------------------Imports---------------------------------
import logging
import aiohttp
import discord
import asyncio
import json
from discord.ext import commands
from datetime import datetime as dt
import fmtjson

# ---------------------------Logs------------------------------------
def commandinfo(ctx):
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Command Used; '
                 f'Server_id: {ctx.message.server.id} '
                 f'Author_id: {ctx.message.author.id} '
                 f'Invoke: {ctx.message.content}')

def changedefault(ctx):
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Default Changed; '
                 f'Server_id: {ctx.message.server.id} '
                 f'Author_id: {ctx.message.author.id} '
                 f'Invoke: {ctx.message.content}')

def taskcomplete():
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Task completed successfully!')

def catchlog(exception):
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Exception Caught: {exception}')

# ---------------------------Checks----------------------------------
def admin_check():
    def predicate(ctx):
        return ctx.message.author.server_permissions.administrator
    return commands.check(predicate)

# ---------------------------Tasks-----------------------------------
async def getposts():
    """
    This function is the task that gets reddit posts on a 5 minute timer.
    """
    # wait to run task till bot is ready.
    await bot.wait_until_ready()

    while True:
        now = dt.utcnow()
        for id in data:
            # get default posting channel from json file
            destination = bot.get_channel(data[id]['default_channel'])

            # reddits that the server is watching
            reddits = list(data[id]['watching'])

            # # store nsfw filter
            # nsfwfilter = data[id]['NSFW_filter']
            #
            # store channel creation option
            create = data[id]['create_channel']

            # Don't do anything if the bot can't find reddits or a destination.
            if destination == None or reddits == None:
                break

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

                # TODO: Check for NSFW posts.
                # posts[0]['over_18'] == True for nsfw reddits

                for x in posts:
                    posttime = dt.utcfromtimestamp(x['created_utc'])
                    # if 300 can't go into total seconds difference once, it gets added to the list of urls
                    if (((now - posttime).total_seconds()) / 300) <= 1:
                        images.append(x['url'])

                    # I'm pretty sure this code does nothing.
                    if not images:
                        await asyncio.sleep(1)
                        break

                # TODO: Function this to make easier if the bot is supposed to post in a specific channel
                # TODO: Make all links post at the same time to avoid ratelimit?

                if create == 0:
                    for image in images:
                        await bot.send_message(destination, f'From r/{reddit} ' + image)
                        await asyncio.sleep(1) # sleep for 1 second to help prevent the ratelimit from being reached.
                elif create == 1:
                    sendto = discord.utils.get(bot.get_all_channels(), name=str.lower(str(reddit)))

                    # If channel is not found, it applies NoneType. This statement creates the channel.
                    # The sleep is required because if the bot goes too fast, it can't find the channel,
                    # even though it exists.
                    if sendto is None:
                        await bot.create_channel(bot.get_server(data[id]['id']),
                                                     name=str(reddit),
                                                     type=discord.ChannelType.text)
                        await asyncio.sleep(5)
                        # reassign's sendto so that it is no longer NoneType
                        sendto = discord.utils.get(bot.get_all_channels(), name=str.lower(str(reddit)))

                        await bot.send_message(sendto, '\n'.join(images))

        taskcomplete()
        await asyncio.sleep(300) # sleep for 5 minutes before it repeats the process

# -------------------Other-Functions---------------------------------
async def respcheck(url):
    """
    used for checking if posts exist for *sub command(subscribe function)
    This is only temporary till I can make it a more universal function.
    :param url:
    :return:
    """
    # TODO: Make this work with getposts task.
    posts = []
    with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                json = await resp.json()
                posts = json['data']['children']

    return posts

# ---------------------------BOT-------------------------------------
bot = commands.Bot(command_prefix = '*')

# ---------------------------Events----------------------------------
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Type *help for help'))

@bot.event
async def on_server_join(server):
    """
    When the bot joins a server, it will set defaults in the json file and pull all info it needs.
    :param server:
    :return:
    """
    pass

'''
@bot.event
async def on_command_error(error, ctx)
    pass
    
@bot.event
async def on_command_completion(ctx)
    """
    This is pretty much just a logger when a command is used. 
    """
    pass
'''

# -------------------------Commands----------------------------------

@bot.command(pass_context = True, name = 'get', hidden = True)
async def getPosts(ctx, reddit, sort):
    """
    I'm not sure what i'm using this command for. hidden for now.
    :param ctx:
    :param reddit:
    :param sort:
    :return:
    """
    pass

@bot.group(pass_context = True, name = 'default')
@admin_check()
async def setDefaults(ctx):
    """
    base command to call subcommands to set defaults for the server.
    :param ctx:
    :return:
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No subcommands invoked.')
        commandinfo(ctx)

@setDefaults.command(pass_context = True, name = 'channel')
@admin_check()
async def defaultChannel(ctx, channel):
    """
    set default channel
    :param ctx:
    :param channel:
    :return:
    """
    newchannel = discord.utils.get(bot.get_all_channels(), name = channel)

    for server in data:
        sid = ctx.message.server.id
        if str(sid) == data[server]['id']:
            data[server]['default_channel'] = newchannel.id
            await bot.say(f"default channel changed to {newchannel.mention}\n"
                          f"You will notice this change when I scour reddit again.")

            fmtjson.edit_json('options', data)

            break

        else:
            continue

    changedefault(ctx)

@bot.command(pass_context = True, name = 'sub')
@admin_check()
async def subscribe(ctx, subreddit):
    """
    command to 'subscribe' to a subreddit. aka watch for new posts
    :param ctx:
    :param subreddit:
    :return:
    """
    url = f"https://www.reddit.com/r/{subreddit}/new/.json"
    posts = await respcheck(url)

    if posts:
        for server in data:
            sid = ctx.message.server.id
            if str(sid) == data[server]['id']:
                subs = data[server]['watching']
                subs.append(subreddit)
                data[server]['watching'] = subs
                await bot.say(f'Subreddit: {subreddit} added!\n'
                              f'You will notice this change when I scour reddit again.')

                fmtjson.edit_json('options', data)
                break

    # TODO: Make reachable.
    else:
        await bot.say(f'Sorry, I can\'t reach {subreddit}. '
                      f'Check your spelling or make sure that the reddit actually exists.')


@bot.command(pass_context = True, name = 'unsub')
@admin_check()
async def unsub(ctx, subreddit):
    """
    unsubscribes from a specified subreddit. 
    :param ctx:
    :param subreddit:
    :return:
    """
    for server in data:
        sid = ctx.message.server.id
        if str(sid) == data[server]['id']:
            subs = data[server]['watching']
            if subreddit in subs:
                subs.remove(subreddit)
                data[server]['watching'] = subs
                await bot.say(f'Subreddit: {subreddit} removed!\n'
                              f'You will notice this change when I scour reddit again.')
                fmtjson.edit_json('options', data)
                break

            else:
                await bot.say(f'Subreddit: {subreddit} not found. Please make sure you are spelling'
                              f' it correctly.')
                break

        else:
            continue

@bot.command(pass_context = True, name = 'listsubs')
async def listsubs(ctx):
    """
    shows a list of subreddits that the bot is watching for the server.
    :param ctx:
    :return:
    """
    for server in data:
        sid = ctx.message.server.id
        if str(sid) == data[server]['id']:
            subs = data[server]['watching']
            strsub = ''
            for sub in subs:
                strsub += f'r/{sub}\n'

            await bot.say(f"This server is subbed to:\n{strsub}")

# ---------------------------Run-------------------------------------
if __name__ == '__main__':
    # get token
    with open('token.txt') as token:
        token = token.readline()

    # Start Logging
    logging.basicConfig(handlers=[logging.FileHandler('discord.log', 'a', 'utf-8')],
                        level=logging.INFO)

    data = fmtjson.read_json('options')

    # run bot/start loop
    try:
        bot.loop.create_task(getposts())
        bot.loop.run_until_complete(bot.run(token.strip()))
    except Exception as e:
        catchlog(e)
