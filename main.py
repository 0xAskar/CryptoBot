import bot_ids
import os
import bot_class
from bot_class import discord_bot
from dotenv import load_dotenv
import asyncio
import discord
import logging
import datetime
from discord.ext import tasks, commands
from discord.ext.tasks import loop
from discord.ext import commands
import urllib.request
import requests
from urllib.request import Request, urlopen
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

if __name__ == "__main__":
    # main variables
    bot_token = bot_ids.bot_token_real
    bot_id = bot_ids.bot_id_real
    askar_id = 372010870756081675
    guild_p = "/r/Pennystocks"
    bot_name = ""
    bot_member = None
    askar_member = None
    askar_name = ""
    last_fetch_time = ""
    last_contract = "tst"
    logging.basicConfig(filename="log.log", level=logging.INFO)

    # load up the coingecko, etherscan, and discord api's
    load_dotenv()

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents = intents)

    db = discord_bot()
    print(db.cg.ping())
    # main functions that need to run

    @loop(seconds=20.0)
    async def background_task():
        try:
            await bot.wait_until_ready()
            bot_list = []
            for guild in bot.guilds:
                for member in guild.members:
                    if member.id == bot_id:
                        bot_member = member
                        bot_name = member.name
                        bot_list.append(bot_member)
                    if member.id == askar_id:
                        askar_member = member
                        askar_name = member.name
            # update the name to the price of bitcoin and the status to the price of eth
            logging.info(db.cg.ping())
            # update all the bot in each server
            for bot_x in bot_list:
                await bot_x.edit(nick = db.btc_status())
                await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= db.eth_status()))
            logging.info("Finished Updating Bot")
            global last_fetch_time
            last_fetch_time = datetime.datetime.now()
        except:
            print("Unsuspected error")
            print(datetime.datetime.now())

    @bot.event
    async def on_ready():
        bot_list = []
        bot_names = []
        for guild in bot.guilds:
            members = '\n - '.join([member.name for member in guild.members])
            ids = [member.id for member in guild.members]
            for member in guild.members:
                if member.id == bot_id:
                    bot_member = member
                    bot_name = member.name
                    bot_list.append(bot_member)
                    bot_names.append(bot_name)
                if member.id == askar_id:
                    askar_member = member
                    askar_name = member.name
        bot_count = 0
        print(f"{bot_names[0]} (x" + str(len(bot_names)) + ") has connected to Discord!")
        global last_fetch_time
        last_fetch_time = datetime.datetime.now()

    @bot.event
    async def on_message(message):
        # retrieve message
        info = message.content
        command = ""
        info = info.lower()
        # if message is from a bot, return
        if message.author == bot.user:
            return
        # if message begins with "!"
        if len(info) > 0  and info[0] == '!':
            #  parse out "!", and separate into string array
            command = info[1:]
            str_divide = command.split()
            if len(str_divide) < 1:
                return
            # if user asks for help on commands
            if command == "crypto-help":
                response = db.help
                suggester = db.find_member(bot, guild_p, message.author.id)
                await suggester.send(response)
                await message.add_reaction('\N{THUMBS UP SIGN}')
            # if user wants to send a suggestion
            elif str_divide[0] == "suggestion" or str_divide[0] == "suggestions":
                if len(str_divide) > 1:
                    user = db.find_member(bot, guild_p, askar_id)
                    suggester = db.find_member(bot, guild_p, message.author.id)
                    await user.send("suggestion" + " by " + suggester.name + ": " + command[11:])
                    suggester = db.find_member(bot, guild_p, message.author.id)
                    await suggester.send("```Your suggestion was sent```")
                    await message.add_reaction('\N{THUMBS UP SIGN}')
                else:
                    await message.channel.send("```Invalid Suggestion: There was no suggestion```")
            # if user requests a line chart of a coin
            elif str_divide[0] == "chart":
                if len(str_divide) == 4:
                    # line_output = db.get_line_chart_two(str_divide[1], str_divide[2],str_divide[3])
                    line_output = db.get_line_chart(str_divide[1], str_divide[2], str_divide[3], 2)
                    if line_output == "":
                        await message.channel.send(file = discord.File('chart.png'))
                    else:
                        await message.channel.send(embed = db.error())
                # check for default and also make default for chart coin1 coin2
                elif len(str_divide) == 3:
                    # check to see if theyre doing a normal one coin chart or nto
                    if str_divide[2].isdigit() or str_divide[2] == "max":
                        line_output = db.get_line_chart(str_divide[1], "", str_divide[2], 1)
                        if line_output == "":
                            await message.channel.send(file = discord.File('chart.png'))
                        else:
                            await message.channel.send(embed = db.error())
                    # if not, then they are trying to do default two coin chart
                    else:
                        line_dual_output = db.get_line_chart(str_divide[1], str_divide[2], "30", 2)
                        if line_dual_output == "":
                            await message.channel.send(file = discord.File('chart.png'))
                        else:
                            await message.channel.send(embed = db.error())
                # if user doesn't specify num days, default to 30
                elif len(str_divide) == 2:
                    line_output = db.get_line_chart(str_divide[1], "", "30", 1)
                    if line_output == "":
                        await message.channel.send(file = discord.File('chart.png'))
                    else:
                        await message.channel.send(embed = db.error())
                else:
                    await message.channel.send(embed = db.error())
                    return
            # if user requests candle chart of a coin
            elif str_divide[0] == "candle":
                if len(str_divide) == 3 and str(str_divide[2]).isdigit():
                    candle_output = db.get_candle_chart(str_divide[1], str_divide[2])
                    if candle_output == "":
                        embedImage = discord.Embed(color=0x4E6F7B) #creates embed
                        embedImage.set_image(url="attachment://candle.png")
                        await message.channel.send(file = discord.File("candle.png"), embed = embedImage)
                    elif candle_output == "error":
                        await message.channel.send(embed = db.error())
                    else:
                        await message.channel.send(candle_output)
                # if user doesn't specify num days, default to 30
                elif len(str_divide) == 2:
                    candle_output = db.get_candle_chart(str_divide[1], "30")
                    if candle_output == "":
                        embedImage = discord.Embed(color=0x4E6F7B) #creates embed
                        embedImage.set_image(url="attachment://candle.png")
                        await message.channel.send(file = discord.File("candle.png"), embed = embedImage)
                    elif candle_output == "error":
                        await message.channel.send(embed = db.error())
                    else:
                        await message.channel.send(candle_output)
                else:
                    await message.channel.send(embed = db.error())
            # if user wants to check conversion rates
            elif str_divide[0] == "convert":
                if len(str_divide) == 4 and str(str_divide[1]).isdigit():
                    convert_output = db.get_conversion(str_divide[1], str_divide[2], str_divide[3])
                    if convert_output != "e":
                        await message.channel.send(embed = convert_output)
                    else:
                        await message.channel.send(embed = db.error())
                elif len(str_divide) == 3:
                    convert_output = db.get_conversion(1, str_divide[1], str_divide[2])
                    if convert_output != "e":
                        await message.channel.send(embed = convert_output)
                    else:
                        await message.channel.send(embed = db.error())
                else:
                    await message.channel.send(embed = db.error())
            elif str_divide[0] == "supply":
                supply_output = db.get_supply(str_divide[1])
                if supply_output != "e":
                    await message.channel.send(embed = supply_output)
                else:
                    await message.channel.send(embed = db.error())
            elif str_divide[0] == "image":
                image_output = db.get_image(str_divide[1])
                if image_output != "e":
                    embedResponse = discord.Embed(title = image_output, color=0x4E6F7B) #creates embed
                    embedResponse.set_image(url="attachment://image.png")
                    await message.channel.send(file = discord.File("image.png"), embed = embedResponse)
                else:
                    await message.channel.send(embed = db.error())
            elif str_divide[0] == "ath" or str_divide[0] == "atl" or str_divide[0] == "range":
                if str_divide[0] == "ath":
                    output = db.get_all_time("H", str_divide[1])
                    if output != "e":
                        await message.channel.send(embed = output)
                    else:
                        await message.channel.send(embed = db.error())
                elif str_divide[0] == "atl":
                    output = db.get_all_time("L", str_divide[1])
                    if output != "e":
                        await message.channel.send(embed = output)
                    else:
                        await message.channel.send(embed = db.error())
                elif str_divide[0] == "range":
                    output = db.get_all_time("R", str_divide[1])
                    if output != "e":
                        await message.channel.send(embed = output)
                    else:
                        await message.channel.send(embed = db.error())
            elif str_divide[0] == "tvl-ratio":
                print("in here")
                output = db.get_mcap_to_tvl_ratio(str_divide[1])
                await message.channel.send(embed = output)
            elif str_divide[0] == "tvl":
                output = db.get_tvl(str_divide[1])
                await message.channel.send(embed = output)
            # if user's request has more than one string, send error
            elif len(str_divide) > 1:
                # ignores commands about coins
                for word in useless_words:
                    if str_divide[0] == word:
                        pass
                else:
                    await message.channel.send(embed = db.error())
            elif len(str_divide) == 1:
                # if user wants events
                # if command == "events":
                #     await message.channel.send(db.get_events())
                # elif command == 'global':
                #     get_global_data()
                # if user wants eth gas prices
                if command == "gas":
                    await message.channel.send(embed = db.gas())
                # if user wants to get the knowledge of shi's shitcoin
                elif command == "fetch":
                    await message.channel.send(last_fetch_time)
                elif command == "trendy":
                    await message.channel.send(embed = db.get_trending())
                elif command == 'future':
                    await message.channel.send(db.future())
                # if user wants info about global defi stats
                elif command == 'global-defi':
                    await message.channel.send(db.get_global_defi_data())
                elif command == "defisocks":
                    await message.channel.send("Unavailable")
                    db.get_ds()
                    embedResponse = discord.Embed(color=0x4E6F7B) #creates embed
                    embedResponse.add_field(name= "Defisocks", value = "Price and Supply of Defisocks", inline=False)
                    embedResponse.set_image(url="attachment://ds.png")
                    await message.channel.send(file = discord.File("ds.png"), embed = embedResponse)
                # if user wants info about exchanges
                elif command == 'list-exchanges':
                    await message.channel.send(db.get_list_exchanges())
                elif command == 'grm-chart':
                    db.get_gmr()
                    embedResponse = discord.Embed(color=0x4E6F7B) #creates embed
                    embedResponse.add_field(name= "Golden Ratio Multiple Chart", value = "Multiple: Ma_350 * (1.6, 2, 3, 5, 8, 13, 21)", inline=False)
                    embedResponse.set_image(url="attachment://grm.png")
                    await message.channel.send(file = discord.File("grm.png"), embed = embedResponse)
                elif command == 'mvrv-chart':
                    db.get_mvrv()
                    embedResponse = discord.Embed(color=0x4E6F7B) #creates embed
                    embedResponse.add_field(name= "MVRV Z-Score ", value = "Score: (Market_cap - realized_cap) / StdDev(Market_cap)", inline=False)
                    embedResponse.set_image(url="attachment://mvrv.png")
                    await message.channel.send(file = discord.File("mvrv.png"), embed = embedResponse)
                elif command == 'puell-chart':
                    db.get_puell()
                    embedResponse = discord.Embed(color=0x4E6F7B) #creates embed
                    embedResponse.add_field(name= "Puell Multiple Chart", value = "Multiple: Daily Coin Insurrance / MA_365 (Daily Coin Insurrance)", inline=False)
                    embedResponse.set_image(url="attachment://puell.png")
                    await message.channel.send(file = discord.File("puell.png"), embed = embedResponse)
                elif command == 'pi-chart':
                    db.get_pi()
                    embedResponse = discord.Embed(color=0x4E6F7B) #creates embed
                    embedResponse.add_field(name= "Pi Cycle Top Indicator Chart", value = "Value: MA_365*2 and MA_111", inline=False)
                    embedResponse.set_image(url="attachment://picycle.png")
                    await message.channel.send(file = discord.File("picycle.png"), embed = embedResponse)
                # if user wants info about any coin
                else:
                    result = db.get_coin_price(command)
                    if result == "":
                        await message.channel.send(embed = db.error())
                    else:
                        await message.channel.send(embed = db.get_coin_price(command))
            else:
                    await message.channel.send(embed = db.error())

    # run background task and bot indefintely
    background_task.start()
    bot.run(bot_token)
