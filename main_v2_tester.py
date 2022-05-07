import bot_ids
import os
import bot_class
from bot_class import discord_bot
from dotenv import load_dotenv
import asyncio
import discord
from discord import app_commands
import datetime
from discord.ext import tasks, commands
from discord.ext.tasks import loop
import sys
import urllib.request
import requests
from urllib.request import Request, urlopen
import praw
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import bot_ids
import crypto_commands


if __name__ == "__main__":
    # main variables
    bot_token = bot_ids.bot_token_tester
    bot_id = bot_ids.bot_id_tester
    askar_id = 372010870756081675
    bot_name = ""
    bot_member = None
    askar_member = None
    askar_name = ""
    last_fetch_time = ""
    count = 0
    guild_id = 769635647782256690
    guild_p = "/r/Pennystocks"
    guild_pp = "Playground"
    app_id = 778833473913225216



    # load up the coingecko, etherscan, and discord api's
    load_dotenv()
    db = discord_bot()
    print(db.cg.ping())

    class MainBot(commands.Bot):
        # initialize the bot
        def __init__(self):
            intents = discord.Intents.all()
            super().__init__(command_prefix='!', intents = intents, application_id = app_id)
            self.initial_extensions = [
                'crypto_commands'
            ]
        # add the background task
        async def setup_hook(self):
            self.background_task.start()
            for ext in self.initial_extensions:
                await self.load_extension(ext)
        # create background loop to update bot information
        @tasks.loop(seconds = 10)
        async def background_task(self):
            await self.wait_until_ready()
            bot_list = []
            global count
            try:
                # change presence globally
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= db.eth_status()))
                # however, because we are restricted to changing usernames often
                # we need to change nicknames which are a guild-by-guild basis
                for guild in self.guilds:
                    await guild.me.edit(nick = str(count))
                count += 1
                global last_fetch_time
                last_fetch_time = datetime.datetime.now()
            except Exception as err:
                print(err)
                print("Unsuspected error")
                print(datetime.datetime.now())

        async def on_ready(self):
            print("Ready!")

    # create instance of bot class
    bot_class = MainBot()

    ############## Create Commands #################
    @bot_class.command()
    async def fake_command(ctx):
        print("ran command")
        bot_class.tree.copy_global_to(guild = discord.Object(id = guild_id))
        await bot_class.tree.sync(guild = discord.Object(id = guild_id))

    bot_class.run(bot_token)
