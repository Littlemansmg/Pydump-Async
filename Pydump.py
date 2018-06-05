"""
Pydump-Rewrite by Scott 'LittlemanSMG' Goes on 5/24/18 (not actual date, just the date I decided to make this part.
Pydump is a bot that is used to send reddit posts to discord per server.

Using Discord.py
github www.github.com/littlemansmg/Pydump-rewrite
"""
# region -----IMPORTS
import asyncio

import logging
from datetime import datetime as dt

import aiohttp
import discord
from discord.ext import commands

import fmtjson


# endregion

# region -----LOGS
def commandinfo(ctx):
    # log when a command it used
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} COMMAND USED; '
                 f'Server_id: {ctx.message.server.id} '
                 f'Author_id: {ctx.message.author.id} '
                 f'Invoke: {ctx.message.content}')

def changedefault(ctx):
    # log when a default has been changed
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} DEFAULT CHANGED; '
                 f'Server_id: {ctx.message.server.id} '
                 f'Author_id: {ctx.message.author.id} '
                 f'Invoke: {ctx.message.content}')

def taskcomplete():
    # log when the task finishes
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} Task completed successfully!')

def catchlog(exception):
    # General log for exceptions
    now = dt.now().strftime('%m/%d %H:%M')
    logging.info(f'{now} EXCEPTION CAUGHT: {exception}')
# endregion

#region -----CHECKS
def admin_check():
    # check if the user is an admin
    def predicate(ctx):
            return ctx.message.author.server_permissions.administrator
    return commands.check(predicate)

def nopms(ctx):
    # check for no PM's
    if ctx.message.channel.is_private:
        raise commands.NoPrivateMessage
    else:
        return True
# endregion

# region -----TASKS
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

            # get default nsfw channel
            nsfw_channel = bot.get_channel(data[server]['NSFW_channel'])

            # reddits that the server is watching
            reddits = list(data[server]['watching'])

            # store nsfw filter
            nsfwfilter = data[server]['NSFW_filter']

            # store channel creation option
            create = data[server]['create_channel']

            # Don't do anything if the bot can't find reddits or a destination.
            if destination == None:
                continue
            elif reddits == None:
                await bot.send_message(destination, 'I don\'t have any reddits to watch! Type `r/sub <subreddit>` '
                                                    'to start getting posts!')
                continue

            for reddit in reddits:
                url = f"https://www.reddit.com/r/{reddit}/new/.json"
                posts = await respcheck(url)

                if not posts:
                    continue

                images, nsfwimages = await appendimages(posts, now, nsfwfilter, nsfw_channel)

                # This skips to next reddit.
                if not images and not nsfwimages:
                    await asyncio.sleep(1)
                    continue

                if create == 0:
                    if images:
                        for image in images:
                            await bot.send_message(destination, f'From r/{reddit} {image}')
                            await asyncio.sleep(1.5)  # try to prevent the ratelimit from being reached.
                    if nsfwimages:
                        for image in nsfwimages:
                            await bot.send_message(nsfw_channel, f'From r/{reddit} {image}')
                            await asyncio.sleep(1.5)
                elif create == 1 and images:
                    sendto = await createchannel(reddit, data[server]['id'])
                    await bot.send_message(sendto, '\n'.join(images))

        taskcomplete()
        await asyncio.sleep(300) # sleep for 5 minutes before it repeats the process
# endregion

# region -----OTHER-FUNCTIONS
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

async def offjoin(servers):
    for server in servers:
        if not server.id in data.keys():
            data.update(
                {server.id: {
                    'default_channel': server.owner.id,
                    'NSFW_channel': '',
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

async def offremove(servers):
    serverlist = []
    removed = []
    for server in servers:
        serverlist.append(server.id)

    for key in data:
        if not key in serverlist:
            removed.append(key)

    if removed:
        for server in removed:
            data.pop(server, None)
        fmtjson.edit_json('options', data)

async def appendimages(posts, now, nsfwfilter, nsfw_channel):
    images = []
    nsfwimages = []
    for x in posts:
        posttime = dt.utcfromtimestamp(x['created_utc'])
        # if 300 can't go into total seconds difference once, it gets added to the list of urls
        if (((now - posttime).total_seconds()) / 300) <= 1:
            if nsfwfilter == 1:
                if x['over_18'] == True:
                    continue
                else:
                    images.append(x['url'])
            elif nsfwfilter == 0:
                if x['over_18'] == True and nsfw_channel:
                    nsfwimages.append(x['url'])
                    continue
                images.append(x['url'])
    return (images, nsfwimages)

async def createchannel(reddit, server):
    sendto = discord.utils.get(bot.get_all_channels(), name=reddit.lower(), server__id=server)

    if sendto is None:
        await bot.create_channel(
            bot.get_server(server), name=reddit.lower(), type=discord.ChannelType.text
        )
        await asyncio.sleep(5)  # sleep so that the bot has a chance to see the channel
        sendto = discord.utils.get(
            bot.get_all_channels(), name=reddit.lower(), server__id=server
        )
    return sendto

# endregion

# region -----BOT CONTENT
bot = commands.Bot(command_prefix = 'r/')
# Check to prevent user from trying to use commands in a PM
bot.add_check(nopms)

# region -----EVENTS
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='Type r/help for help'))
    await offjoin(bot.servers)
    await offremove(bot.servers)

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
            'NSFW_channel': '',
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
    data.pop(server.id, None)
    fmtjson.edit_json("options", data)

@bot.event
async def on_command_error(error, ctx):
    # when error is raised, this is what happens.
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.channel, 'Stop it, You can\'t use me in a PM. Go into a server.')
        catchlog(error)

    if isinstance(error, commands.CommandInvokeError):
        await bot.send_message(ctx.message.channel, 'You messed up the command. Make sure you are doing it right, '
                                                    'and you are in a discord server I\'m on.')
        catchlog(error)

    if isinstance(error, commands.CommandNotFound):
        await bot.delete_message(ctx.message)
        await bot.send_message(ctx.message.channel, 'Either you didn\'t type a proper command, or you did'
                                                    'but you added a capital letter somewhere. All commands are '
                                                    'lowercase.')
        catchlog(error)
# endregion

# region -----COMMANDS

# region -----DEFAULT COMMAND GROUP
@bot.group(pass_context = True, name = 'default')
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
        commandinfo(ctx)
        ctx.message.content = ctx.prefix + 'help ' + ctx.invoked_with
        await bot.process_commands(ctx.message)

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

    sid = ctx.message.server.id
    data[sid]['default_channel'] = newchannel.id
    await bot.say(f"Default channel changed to {newchannel.mention}\n"
                  f"You will notice this change when I scour reddit again.")
    fmtjson.edit_json('options', data)

    changedefault(ctx)

@setDefaults.command(pass_context = True, name = 'nsfwchannel')
@admin_check()
async def defaultChannel(ctx, channel):
    """
    Set the Default nsfwchannel for the bot to post in.
    Usage: r/default nsfwchannel <channel>
    Permissions required: Administrator
    :param ctx:
    :param channel:
    :return:
    """
    newchannel = discord.utils.get(bot.get_all_channels(), name = channel, server__id = ctx.message.server.id)

    if not newchannel:
        raise commands.CommandInvokeError

    sid = ctx.message.server.id
    data[sid]['NSFW_channel'] = newchannel.id
    await bot.say(f"Default channel changed to {newchannel.mention}\n"
                  f"You will notice this change when I scour reddit again.")
    fmtjson.edit_json('options', data)

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
    sid = ctx.message.server.id
    if data[sid]['NSFW_filter'] == 1:
        data[sid]['NSFW_filter'] = 0
        await bot.say("NSFW filter has been TURNED OFF. Enjoy your sinful images, loser. Also be sure"
                      "to label your default channel or the NSFW reddit channels as NSFW channels.")
    else:
        data[sid]['NSFW_filter'] = 1
        await bot.say("NSFW filter has been TURNED ON. I really don't like looking for those "
                      "images.")
    fmtjson.edit_json('options', data)

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
    sid = ctx.message.server.id
    if data[sid]['create_channel'] == 1:
        data[sid]['create_channel'] = 0
        await bot.say("Creating channels has been TURNED OFF. I will now make all of my posts in "
                      "your default channel.")
    else:
        data[sid]['create_channel'] = 1
        await bot.say("Creating channels has been TURNED ON. I can now create channels for each reddit "
                      "that you are watching.")
    fmtjson.edit_json('options', data)

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
    sid = ctx.message.server.id
    if sid in data.keys():
        channel = bot.get_channel(data[sid]['default_channel'])
        nsfwchannel = bot.get_channel(data[sid]['NSFW_channel'])

        if not nsfwchannel:
            nsfwchannel = 'Nowhere'

        if data[sid]['NSFW_filter'] == 0:
            nsfw = 'OFF'
        else:
            nsfw = 'ON'

        if data[sid]['create_channel'] == 0:
            create = 'OFF'
        else:
            create = 'ON'

        await bot.say(f"Default channel: {channel}\n"
                      f"Default NSFW channel: {nsfwchannel}\n"
                      f"NSFW filter: {nsfw}\n"
                      f"Create channels: {create}")

    changedefault(ctx)

@setDefaults.command(pass_context = True, name = 'all')
@admin_check()
async def defaultall(ctx):
    """
    This command sets all options to their default.
    :param ctx:
    :return:
    """
    sid = ctx.message.server.id
    data[sid]['default_channel'] = ctx.message.server.owner.id
    data[sid]['NSFW_channel'] = ''
    data[sid]['NSFW_filter'] = 1
    data[sid]['create_channel'] = 0
    data[sid]['watching'] = []
    fmtjson.edit_json('options', data)
    await bot.say('All options have been set to their default. Default channel is the server owner, so please use'
                  '`r/default channel <channel name>` EX.`r/default channel general`')

# endregion

# region -----ABOUT COMMAND GROUP
@bot.group(pass_context = True, name = 'about')
async def about(ctx):
    if ctx.invoked_subcommand is None:
        commandinfo(ctx)
        ctx.message.content = ctx.prefix + 'help ' + ctx.invoked_with
        await bot.process_commands(ctx.message)

@about.command(pass_context = True, name = 'bot')
async def botabout(ctx):
    await bot.say('```'
                  'This is a bot developed by LittlemanSMG in python using discord.py v0.16.12\n'
                  'I use a standard json file to store ID\'s and all the options for each server.\n'
                  'Code is free to use/look at, following the MIT lisence at '
                  'www.github.com/littlemansmg/pydump-rewrite \n'
                  'Have any recommendations for/issues with the bot? Open up an Issue on github!\n'
                  '```')
    commandinfo(ctx)

@about.command(pass_context = True, name = 'dev')
async def devabout(ctx):
    await bot.say('```'
                  "I really don't feel like I need this, but here it is. I'm Scott 'LittlemanSMG' Goes, and"
                  "I made this bot on my own, with some help from r/discord_bots discord. Originally, this bot was "
                  "made using Praw, a reddit api wrapper, but ran into some massive blocking issues. There was so many"
                  "issues that I had to remake the bot using aiohttp and it's a much better bot now. "
                  "mee6 has this kind of functionality, but I didn't want to deal with all of mee6. I just wanted "
                  "the reddit portion. The original intention was to streamline my meme consumption, but "
                  "I realised that this bot could be used for more than just memes. All of my work is currently "
                  "on github(www.github.com/littlemansmg. It isn't much because i'm still learning, "
                  "but I am getting better.\n"
                  "```")
    commandinfo(ctx)
# endregion

# region -----OTHER COMMANDS
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

@bot.command(pass_context = True, name = 'sub')
@admin_check()
async def subscribe(ctx, *subreddit):
    """
    This command will 'subscribe' to a reddit and will make posts from it.
    Usage: r/sub <subreddit>
    Permissions required: Administrator
    :param ctx:
    :param subreddit:
    :return:
    """
    sid = ctx.message.server.id
    subs = data[sid]['watching']
    added = []
    for reddit in subreddit:
        url = f"https://www.reddit.com/r/{reddit}/new/.json"
        posts = await respcheck(url)

        if posts:
            if reddit.lower() in subs:
                await bot.say(f'{reddit} is already in your list!')
                continue
            else:
                subs.append(reddit.lower())
                added.append(reddit.lower())
        else:
            await bot.say(f'Sorry, I can\'t reach {reddit}. '
                          f'Check your spelling or make sure that the reddit actually exists.')
    if added:
        data[sid]['watching'] = subs
        await bot.say(f"Subreddit(s): {', '.join(added)} added!\n"
                      f"You will notice this change when I scour reddit again.")

        fmtjson.edit_json('options', data)

    commandinfo(ctx)

@bot.command(pass_context = True, name = 'unsub')
@admin_check()
async def unsub(ctx, *subreddit):
    """
    This command will 'unsubscribe' from a reddit and will no longer make posts.
    Usage: r/unsub <subreddit>
    Permissions required: Administrator
    :param ctx:
    :param subreddit:
    :return:
    """
    sid = ctx.message.server.id
    subs = data[sid]['watching']
    removed = []
    for reddit in subreddit:
        if reddit in subs:
            subs.remove(reddit.lower())
            removed.append(reddit.lower())
        else:
            await bot.say(f'Subreddit: {reddit} not found. Please make sure you are spelling'
                          f' it correctly.')
    if removed:
        data[sid]['watching'] = subs
        await bot.say(f"Subreddit(s): {', '.join(removed)} removed!\n"
                      f"You will notice this change when I scour reddit again.")
        fmtjson.edit_json('options', data)

    commandinfo(ctx)

@bot.command(pass_context = True, name = 'removeall')
async def removeall(ctx):
    """
    This command will "unsubscribe" from all reddits.
    Usage: r/removeall
    Permissions required: Administrator
    :param ctx:
    :return:
    """
    sid = ctx.message.server.id
    data[sid]['watching'] = []
    fmtjson.edit_json('options', data)
    await bot.say('You are no longer subbed to any subreddits! Please don\'t get rid of me. :[')

@bot.command(pass_context = True, name = 'listsubs')
async def listsubs(ctx):
    """
    Shows a list of subreddits that the bot is subscribed to on a server.
    Usage r/listsubs
    :param ctx:
    :return:
    """
    sid = ctx.message.server.id
    subs = data[sid]['watching']
    strsub = ''
    if not subs:
        await bot.say('This server isn\'t subbed to anything. Have an adminstrator type '
                      '`r/sub <subreddit name>` to sub. EX `r/sub funny`')
    else:
        for sub in subs:
            strsub += f'r/{sub}\n'

        await bot.say(f"This server is subbed to:\n{strsub}")

    commandinfo(ctx)
# endregion

# endregion

# endregion

# region -----STARTUP
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
        bot.loop.create_task(getposts())
        bot.loop.run_until_complete(bot.run(token.strip()))
    except Exception as e:
        catchlog(e)
# endregion
