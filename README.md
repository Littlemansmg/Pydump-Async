# Pydump-Async
This bot is built to follow subreddits and send posts to a discord server.
It has various options like a nsfw filter and different viewing options 

## Getting Started
Bot is nearly complete, I just need to get a working url working for it. 

## Current Functionality
* Bot can access Reddit's json object of a subreddit.
* Bot can sort through the json object to find the proper URL and send the URL + the subreddit it came from to discord. 
* Bot can read server settings from json file.
* Bot can set various options
  * Default channel (optional in some cases)
    * Where the bot should send reddit posts
    * Default position is the server owner
  * NSFW filter
    * Filters out what reddit has flaged as over 18 content
    * Default on
    * Toggleable
  * Create channels
    * This option will set if the bot can create a channel for each subreddit it's watching
    * Default off
    * Toggleable
  * Set valid subreddits to 'subscribe' to
    * List of reddits for the bot to check for post from
    * Defaulted to an empty list
  * Set default delay inbetween posts
    * Time (in seconds) how often the bot posts.
    * Defaulted to 5 minutes
* Bot can add/remove a server with set defaults with no user interaction
* All major commands i.e. sub, unsub, toggle nsfw/create are admin only commands

## TODO
*This list is in no particular order.*
* Add more options. (planned below)
  * default sort
  * Allow suggestions / suggestion channel
  * More to come as I think about them
* Set up role based checks. 
  * Ex. Instead of just admins, let people with x role use the command.

## Built With
* [Discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper to run a discord bot in Python.
  * Note: This includes content from [discord-rewrite.py](https://discordpy.readthedocs.io/en/rewrite/index.html).
  Most of this is the documentation for discord.ext.commands
  
