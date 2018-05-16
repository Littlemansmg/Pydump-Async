# Pydump-Rewrite
This bot is built to follow subreddits and send posts to a discord server.
It will have various options that admins can set so personalize what they want the bot to post. 

## Getting Started
The bot is still under heavy development and should not be added to any server as of right now (5/16/18)

## Current Functionality
* Bot can access Reddit's json object of a subreddit from any sort (i.e. new/hot/top).
* Bot can sort through the json object to find the proper URL and send the URL + the subreddit it came from to discord. 
* Bot can read server settings from json file.

## TODO
*This list is in no particular order.*
* Add more options. (planned below)
  * default sort
  * default time to get posts (1min/5min/10min etc.)
    * This includes changing the sleep time so that it runs at the proper times
  * More to come as I think about them
* Find a way to append new servers to the json object with some defaults
* If default_channel is not set, find a way to get a message to the admins to set it. 
* Add commands with proper checks to set options.

## Built With
* [Discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper to run a discord bot in Python.
  * Note: This includes content from [discord-rewrite.py](https://discordpy.readthedocs.io/en/rewrite/index.html).
  Most of this is the documentation for discord.ext.commands
  
