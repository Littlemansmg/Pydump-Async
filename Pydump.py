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
    logging.info(f'{now} COMMAND USED; '
                 f'Server_id: {ctx.message.server.id} '
                 f'Author_id: {ctx.message.author.id} '
                 f'Invoke: {ctx.message.content}')

def changedefault(ctx):
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} DEFAULT CHANGED; '
                 f'Server_id: {ctx.message.server.id} '
                 f'Author_id: {ctx.message.author.id} '
                 f'Invoke: {ctx.message.content}')

def taskcomplete():
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Task completed successfully!')

def catchlog(exception):
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} EXCEPTION CAUGHT: {exception}')

# ---------------------------Checks----------------------------------
def admin_check():
    def predicate(ctx):
            return ctx.message.author.server_permissions.administrator
    return commands.check(predicate)

def nopms():
    def predicate(ctx):
        if ctx.message.channel.is_private:
            raise commands.NoPrivateMessage
        else:
            return True
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
        for server in data:
            # get default posting channel from json file
            destination = bot.get_channel(data[server]['default_channel'])

            # reddits that the server is watching
            reddits = list(data[server]['watching'])

            # store nsfw filter
            nsfwfilter = data[server]['NSFW_filter']

            # store channel creation option
            create = data[server]['create_channel']

            # Don't do anything if the bot can't find reddits or a destination.
            if destination == None:

                break
            elif reddits == None:
                await bot.send_message(destination, 'I don\'t have any reddits to watch! Type `r/sub <subreddit>` '
                                                    'to start getting posts!')
                continue

            for reddit in reddits:
                images = []
                url = f"https://www.reddit.com/r/{reddit}/new/.json"
                posts = await respcheck(url)

                if not posts:
                    continue

                for x in posts:
                    posttime = dt.utcfromtimestamp(x['created_utc'])
                    # if 300 can't go into total seconds difference once, it gets added to the list of urls
                    if (((now - posttime).total_seconds()) / 300) <= 1:
                        if nsfwfilter == 1:
                            if x['over_18'] == True:
                                continue
                            else:
                                images.append(x['url'])
                        else:
                            images.append(x['url'])

                    # This skips to next reddit.
                    if not images:
                        await asyncio.sleep(1)
                        break

                # TODO: Function this to make easier if the bot is supposed to post in a specific channel
                # TODO: Make all links post at the same time to avoid ratelimit?

                if create == 0 and images:
                    for image in images:
                        await bot.send_message(destination, f'From r/{reddit} {image}')
                        await asyncio.sleep(1) # sleep for 1 second to help prevent the ratelimit from being reached.
                elif create == 1 and images:
                    sendto = discord.utils.get(bot.get_all_channels(), name=str.lower(str(reddit)),
                                               server__id = data[server]['id'])

                    # If channel is not found, it applies NoneType. This statement creates the channel.
                    # The sleep is required because if the bot goes too fast, it can't find the channel,
                    # even though it exists.
                    if sendto is None:
                        await bot.create_channel(bot.get_server(data[server]['id']),
                                                     name=str(reddit),
                                                     type=discord.ChannelType.text)
                        await asyncio.sleep(5)
                        # reassign's sendto so that it is no longer NoneType
                        sendto = discord.utils.get(bot.get_all_channels(), name=str.lower(str(reddit)),
                                                   server__id = data[server]['id'])

                    await bot.send_message(sendto, '\n'.join(images))

        taskcomplete()
        await asyncio.sleep(300) # sleep for 5 minutes before it repeats the process

# -------------------Other-Functions---------------------------------
async def respcheck(url):
    """
    This function is used to open up the json file from reddit and get the posts.
    It's used in:
    getposts() - Task
        will continue if no posts are found within 5 minutes
    sub - command
        will tell user if a connection has been made, or if a subreddit exists.
    :param url:
    :return:
    """
    posts = []
    try:
        # Try to open connection to reddit with async
        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:  # 200 == good
                    json = await resp.json()
                    posts = json['data']['children']
                    # puts each post into a dict that can be manipulated
                    posts = list(map(lambda p: p['data'], posts))

    except Exception as e:
        catchlog(e)

    return posts

# ---------------------------BOT-------------------------------------
bot = commands.Bot(command_prefix = 'r/', case_insensitive = True, add_check = nopms())

# ---------------------------Events----------------------------------
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Type r/help for help'))

@bot.event
async def on_server_join(server):
    """
    When the bot joins a server, it will set defaults in the json file and pull all info it needs.

    defaults:
        default channel == 'server owner'
        id == server id
        nsfw filter == 1
        create channel == 0
        watching == []
    :param server:
    :return:
    """

    data.update(
        {server.id: {
            'default_channel': server.owner.id,
            'id': server.id,
            'watching': [],
            'NSFW_filter': 1,
            'create_channel': 0
            }
        }
    )
    fmtjson.edit_json('options', data)

    await bot.send_message(server.owner, 'Thanks for adding me to the server! There are a few things I need '
                                         'from you or your admins to get running though.\n'
                                         'In the discord server(NOT HERE),Please set the default channel for me to '
                                         'post in, or turn on the option for me to create a channel for each '
                                         'subreddit. `r/default channel general` or `r/default create`\n'
                                         'Right now I have the default channel set to PM you, so *I would '
                                         'suggest changing this*. After that, you or your admins '
                                         'can run `r/sub funny` and let the posts flow in!')

@bot.event
async def on_server_remove(server):
    """
    When a bot leaves/gets kicked, remove the server from the .json file.
    :param server:
    :return:
    """
    data.pop(str(server.id), None)

    fmtjson.edit_json("options", data)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.channel, 'Stop it, You can\'t use me in a PM. Go into a server.')
        catchlog(error)

    if isinstance(error, commands.CommandInvokeError):
        await bot.send_message(ctx.message.channel, 'You messed up the command. Make sure you are doing it right, '
                                                    'and you are in a discord server I\'m on.')
        catchlog(error)

    if isinstance(error, commands.CommandNotFound):
        await bot.delete_message(ctx.message)
        await bot.send_message(ctx.message.channel, 'Nope. Not a command.')
        catchlog(error)

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

@bot.group(pass_context = True, name = 'default', case_insensitive = True)
@admin_check()
async def setDefaults(ctx):
    """
    Base command to set the options for a server.
    Usage: r/default
    Permissions required: Administrator
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
    Set the Default channel for the bot to post in.
    Usage: r/default channel <channel>
    Permissions required: Administrator
    :param ctx:
    :param channel:
    :return:
    """
    newchannel = discord.utils.get(bot.get_all_channels(), name = channel, server__id = ctx.message.server.id)

    if not newchannel:
        raise commands.CommandInvokeError

    for server in data:

        sid = ctx.message.server.id
        if str(sid) == data[server]['id']:
            data[server]['default_channel'] = newchannel.id
            await bot.say(f"Default channel changed to {newchannel.mention}\n"
                          f"You will notice this change when I scour reddit again.")
            fmtjson.edit_json('options', data)
            break
        else:
            continue

    changedefault(ctx)

@setDefaults.command(pass_context = True, name = 'nsfw')
@admin_check()
async def nsfwFilter(ctx):
    '''
    Toggles the NSFW filter. DEFAULT: ON
    Usage: r/default nsfw
    Permissions required: Administrator
    :param ctx:
    :return:
    '''
    for server in data:
        toggle = ctx.message.server.id
        if toggle == data[server]['id']:
            if data[server]['NSFW_filter'] == 1:
                data[server]['NSFW_filter'] = 0
                await bot.say("NSFW filter has been TURNED OFF. Enjoy your sinful images, loser.")
            else:
                data[server]['NSFW_filter'] = 1
                await bot.say("NSFW filter has been TURNED ON. I really don't like looking for those "
                              "images.")
            fmtjson.edit_json('options', data)
            break

    changedefault(ctx)

@setDefaults.command(pass_context = True, name = 'create')
@admin_check()
async def createChannels(ctx):
    '''
    Toggles the create channels option. DEFAULT: OFF
    Usage: r/default create
    Permissions required: Administrator
    :param ctx:
    :return:
    '''
    for server in data:
        toggle = ctx.message.server.id
        if toggle == data[server]['id']:
            if data[server]['create_channel'] == 1:
                data[server]['create_channel'] = 0
                await bot.say("Creating channels has been TURNED OFF. I will now make all of my posts in "
                              "your default channel.")
            else:
                data[server]['create_channel'] = 1
                await bot.say("Creating channels has been TURNED ON. I can now create channels for each reddit "
                              "that you are watching.")
            fmtjson.edit_json('options', data)
            break

    changedefault(ctx)

@setDefaults.command(pass_context = True, name = 'show')
@admin_check()
async def showDefaults(ctx):
    '''
    This command will show all defaults for the server.
    Usage: r/default show
    :param ctx:
    :return:
    '''
    for server in data:
        if ctx.message.server.id == data[server]['id']:
            channel = bot.get_channel(data[server]['default_channel'])
            if data[server]['NSFW_filter'] == 0:
                nsfw = 'OFF'
            else:
                nsfw = 'ON'
            if data[server]['create_channel'] == 0:
                create = 'OFF'
            else:
                create = 'ON'

            await bot.say(f"Default channel: {channel.mention}\n"
                    f"NSFW filter: {nsfw}\n"
                    f"Create channels: {create}")
            break

    changedefault(ctx)

@bot.command(pass_context = True, name = 'sub')
@admin_check()
async def subscribe(ctx, subreddit):
    """
    This command will 'subscribe' to a reddit and will make posts from it.
    Usage: r/sub <subreddit>
    Permissions required: Administrator
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
                if subreddit.lower in subs:
                    await bot.say(f'{subreddit} is already in your list!')
                    break
                subs.append(subreddit.lower())
                data[server]['watching'] = subs
                await bot.say(f'Subreddit: {subreddit} added!\n'
                              f'You will notice this change when I scour reddit again.')

                fmtjson.edit_json('options', data)
                break
    else:
        await bot.say(f'Sorry, I can\'t reach {subreddit}. '
                      f'Check your spelling or make sure that the reddit actually exists.')

    commandinfo(ctx)


@bot.command(pass_context = True, name = 'unsub')
@admin_check()
async def unsub(ctx, subreddit):
    """
    This command will 'unsubscribe' from a reddit and will no longer make posts.
    Usage: r/unsub <subreddit>
    Permissions required: Administrator
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

    commandinfo(ctx)

@bot.command(pass_context = True, name = 'listsubs')
async def listsubs(ctx):
    """
    Shows a list of subreddits that the bot is subscribed to on a server.
    Usage r/listsubs
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

    commandinfo(ctx)

# ---------------------------Run-------------------------------------
if __name__ == '__main__':
    # get token
    with open('token.txt') as token:
        token = token.readline()

    # Start Logging
    logging.basicConfig(handlers=[logging.FileHandler('discord.log', 'a', 'utf-8')],
                        level=logging.INFO)
    try:
        data = fmtjson.read_json('options')
    except Exception as e:
        catchlog(e)

    # run bot/start loop
    try:
        # bot.loop.create_task(getposts())
        bot.loop.run_until_complete(bot.run(token.strip()))
    except Exception as e:
        catchlog(e)
