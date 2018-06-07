
# probsjustin code
async def my_background_task(server):
    await bot.wait_until_ready()
    destination = bot.get_channel(data[server]['default_channel'])
    delay = int(data[server]['delay'])
    while not bot.is_closed:


        await asyncio.sleep(delay)  #task runs every time delayed

@bot.event
async def on_ready():
    for server in bot.servers:
        asyncio.ensure_future(my_background_task(server))