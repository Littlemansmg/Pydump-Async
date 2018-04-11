import logging
import aiohttp
import discord
from discord.ext import commands

with open('token.txt') as token:
    token = token.readline()

bot = commands.Bot(command_prefix = '*')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('----------')

log = logging.getLogger('discord')

fancy_name = "Reddit"

message_format = "`New post from /r/{subreddit}`\n\n"\
                 "**{title}** *by {author}*\n"\
                 "{content}\n"\
                 "**Link** {link} \n \n"

async def get_posts(self, subreddit):
    """Gets the n last posts of a subreddit
    Args:
        subreddit: Subbredit name
        n: The number of posts you want
    Returns:
        A list of posts
    """

    url = "https://www.reddit.com/r/{}/new.json".format(subreddit)
    posts = []

    try:
        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    json = await resp.json()
                    posts = json['data']['children']
                    posts = list(map(lambda p: p['data'], posts))
    except Exception as e:
        log.info("Cannot get posts from {}".format(subreddit))
        log.info(e)
        return []

    return posts[:2]

async def display_posts(posts):
    """Display a list of posts into the corresponding destination channel.
    This function only displays posts that hasn't been posted previously.
    """
    for subreddit, posts in posts.items():
        subreddit_posts = reversed(posts)
        for post in subreddit_posts:

            selftext = post['selftext'] or ""
            message = "http://redd.it/"+post['id']
    return message

@bot.command(pass_context = True, name = 'get')
async def getPosts(ctx):
    destination = ctx.message.channel
    bot.send_message(destination, display_posts(get_posts(None, 'dankmemes')))

bot.run(token.strip())
