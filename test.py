import json
import aiohttp
import discord
import asyncio
from collections import defaultdict

with open('options.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

print(len(data["0"]))