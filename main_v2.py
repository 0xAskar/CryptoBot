import bot_ids
import os
import bot_class
from bot_class import discord_bot
from dotenv import load_dotenv
import asyncio
import discord
import datetime
from discord.ext import tasks, commands
from discord.ext.tasks import loop
import sys
import urllib.request
import requests
from urllib.request import Request, urlopen
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import bot_ids

if __name__ == "__main__":
    # main variables
    bot_token = bot_ids.bot_token_real_first_half + bot_ids.bot_token_real_second_half
    bot_id = bot_ids.bot_id_real
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
    app_id = 769265839584051200

    # load up the coingecko, etherscan, and discord api's
    load_dotenv()
    db = discord_bot()
    # print(db.cg.ping())

    def suggestSlash(slash_command):
        embedResponse = discord.Embed(color = 0xF93A2F)
        invite_link = "https://discord.com/api/oauth2/authorize?client_id=769265839584051200&permissions=416008371392&scope=bot%20applications.commands"
        discord_rules = "https://support-dev.discord.com/hc/en-us/articles/4404772028055"
        explanation = "We are transitioning to **slash commands** due to Discord rules. [Learn more](" + discord_rules + ")"
        explanation2 = "1) Admins need to re-add the bot (no need to kick the bot) via this [link](" + invite_link + ")" + "\n" + "2) Use only slash commands. For this, " + slash_command
        explanation3 = "[Join our discord](" + "https://discord.gg/QjUW5uspnA" + ") or message @Askar#1000"
        embedResponse.add_field(name = "IMPORTANT changes for bot commands!", value = str(explanation), inline=False)
        embedResponse.add_field(name = "How to avoid this warning?", value = explanation2, inline=False)
        embedResponse.add_field(name = "Questions?", value = str(explanation3), inline=False)
        try:
            embedResponse.set_footer(text = "Powered by http://cryptobot.info", icon_url = bot_ids.twitter_logo_url)
        except:
            embedResponse.set_footer(text = "Powered by http://cryptobot.info")
        return embedResponse

    class MainBot(commands.Bot):
        # initialize the bot
        def __init__(self):
            intents = discord.Intents.all()
            super().__init__(command_prefix='?', intents = intents, application_id = app_id)
            self.initial_extensions = [
                'crypto_commands'
            ]
        # add the background task
        async def setup_hook(self):
            self.background_task.start()
            for ext in self.initial_extensions:
                await self.load_extension(ext)
        # create background loop to update bot information
        @tasks.loop(seconds = 60)
        async def background_task(self):
            await self.wait_until_ready()
            print("running background task" + str(datetime.datetime.now()))
            bot_list = []
            global count
            try:
                # change presence globally
                eth_status = db.eth_status()
                print("eth status: " + eth_status + " at " + str(datetime.datetime.now()))
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= eth_status))
                # however, because we are restricted to changing usernames often
                # we need to change nicknames which are a guild-by-guild basis
                btc_status = db.btc_status()
                print("btc status: " + btc_status + " at " + str(datetime.datetime.now()))
                for guild in self.guilds:
                    await guild.me.edit(nick = btc_status)
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
    print(bot_class)

    # do this to update all the guilds
    @bot_class.command()
    async def all_tree(ctx):
        print("ran command")
        for guild in bot_class.guilds:
            bot_class.tree.copy_global_to(guild = discord.Object(id = guild.id))
            await bot_class.tree.sync(guild = discord.Object(id = guild.id))


    @bot_class.event
    async def on_message(message):
        # retrieve message
        info = message.content
        useless_words = ["future", "bought", "ban", "mute", "sold", "undo", "rank", "tempmute", "whois"]
        command = ""
        info = info.lower()
        # if message is from a bot, return
        if message.author == bot_class.user:
            return
        # if message begins with "!"
        if len(info) > 0  and info[0] == '!':
            #  parse out "!", and separate into string array
            correct_check = False
            command = info[1:]
            str_divide = command.split()

            if str_divide[0] == "all_tree":
                for guild in bot_class.guilds:
                    try:
                        bot_class.tree.copy_global_to(guild = discord.Object(id = guild.id))
                        await bot_class.tree.sync(guild = discord.Object(id = guild.id))
                        print("updated for: ", guild.id)
                    except Exception as err:
                        print(err)
                        print("Did not add for: ", guild.id)

            if len(str_divide) < 1:
                return
            # if user asks for help on commands
            if command == "crypto-help" or command == "help" or command == "chelp":
                embedResponse = discord.Embed(title = "CryptoBot Site", url = "http://cryptobot.info", color= 0x4E6F7B)
                embedResponse.set_footer(text = "Powered by cryptobot.info")
                await message.channel.send(embed = embedResponse);
                correct_check = True
            # if user wants to send a suggestion
            # elif str_divide[0] == "suggestion" or str_divide[0] == "suggestions":
            #     if len(str_divide) > 1:
            #         user = db.find_member(bot, guild_p, askar_id)
            #         suggester = db.find_member(bot, guild_p, message.author.id)
            #         await user.send("suggestion" + " by " + suggester.name + ": " + command[11:])
            #         suggester = db.find_member(bot, guild_p, message.author.id)
            #         await suggester.send("```Your suggestion was sent```")
            #         await message.add_reaction('\N{THUMBS UP SIGN}')
            #         correct_check = True
            #     else:
            #         await message.channel.send("```Invalid Suggestion: There was no suggestion```")
            # if user requests a line chart of a coin
            elif str_divide[0] == "chart":
                if len(str_divide) == 4:
                    # line_output = db.get_line_chart_two(str_divide[1], str_divide[2],str_divide[3])
                    line_output = db.get_line_chart(str_divide[1], str_divide[2], str_divide[3], 2)
                    warning = suggestSlash("`/chart2 [coin] [coin_2] [num_days]`")
                    await message.channel.send(embed = warning)
                    if line_output != "error":
                        await message.channel.send(file = discord.File('chart.png'), embed = line_output)
                        correct_check = True
                    else:
                        await message.channel.send(embed = db.error())
                # check for default and also make default for chart coin1 coin2
                elif len(str_divide) == 3:
                    # check to see if theyre doing a normal one coin chart or nto
                    if str_divide[2].isdigit() or str_divide[2] == "max":
                        line_output = db.get_line_chart(str_divide[1], "", str_divide[2], 1)
                        warning = suggestSlash("`/chart [coin] [num_days]`")
                        await message.channel.send(embed = warning)
                        if line_output != "error":
                            await message.channel.send(file = discord.File('chart.png'), embed = line_output)
                            correct_check = True
                        else:
                            await message.channel.send(embed = db.error())
                    # if not, then they are trying to do default two coin chart
                    else:
                        line_dual_output = db.get_line_chart(str_divide[1], str_divide[2], "30", 2)
                        if line_dual_output == "":
                            await message.channel.send(file = discord.File('chart.png'))
                            correct_check = True
                        else:
                            await message.channel.send(embed = db.error())
                # if user doesn't specify num days, default to 30
                elif len(str_divide) == 2:
                    line_output = db.get_line_chart(str_divide[1], "", "30", 1)
                    # warning = suggestSlash("`/chart [coin] [num_days]`")
                    # await message.channel.send(embed = warning)
                    if line_output != "error":
                        await message.channel.send(file = discord.File('chart.png'), embed = line_output)
                        correct_check = True
                    else:
                        await message.channel.send(embed = db.error())
                        correct_check = True
                else:
                    await message.channel.send(embed = db.error())
                    return
            # if user requests candle chart of a coin
            elif str_divide[0] == "list" and len(str_divide) > 2:
                suggester = db.find_member(bot_class, guild_p, message.author.id)
                for coin in str_divide:
                    if coin != "list":
                        result = db.get_coin_price(coin)
                        correct_check = True
                        if result == "":
                            await message.channel.send(embed = db.error())
                        else:
                            await suggester.send(embed = db.get_coin_price(coin))
                            correct_check = True
                await message.add_reaction('\N{THUMBS UP SIGN}')
            elif str_divide[0] == "tvl-chart" or str_divide[0] == "tvlc" or str_divide[0] == "ctvl":
                if len(str_divide) == 3:
                    # line_output = db.get_line_chart_two(str_divide[1], str_divide[2],str_divide[3])
                    ctvl_output = db.get_tvl_chart(str_divide[1], "", str_divide[2], 1)
                    if ctvl_output == "":
                        await message.channel.send(file = discord.File('ctvl.png'))
                        correct_check = True
                    elif ctvl_output == "error":
                        await message.channel.send(embed = db.error())
                    else:
                        await message.channel.send(ctvl_output)
                        correct_check = True
                elif len(str_divide) == 2:
                    ctvl_output = db.get_tvl_chart(str_divide[1], "", "1m", 1)
                    if ctvl_output == "":
                        await message.channel.send(file = discord.File('ctvl.png'))
                        correct_check = True
                    elif ctvl_output == "error":
                        await message.channel.send(embed = db.error())
                    else:
                        await message.channel.send(ctvl_output)
                        correct_check = True
            elif str_divide[0] == "candle":
                if len(str_divide) == 3 and str(str_divide[2]).isdigit():
                    candle_output = db.get_candle_chart(str_divide[1], str_divide[2])
                    correct_check = True
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
                    correct_check = True
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
                    correct_check = True
                    if convert_output != "e":
                        await message.channel.send(embed = convert_output)
                    else:
                        await message.channel.send(embed = db.error())
                elif len(str_divide) == 3:
                    convert_output = db.get_conversion(1, str_divide[1], str_divide[2])
                    correct_check = True
                    if convert_output != "e":
                        await message.channel.send(embed = convert_output)
                    else:
                        await message.channel.send(embed = db.error())
                else:
                    await message.channel.send(embed = db.error())
            elif str_divide[0] == "supply":
                supply_output = db.get_supply(str_divide[1])
                warning = suggestSlash("`/supply [coin]`")
                await message.channel.send(embed = warning)
                correct_check = True
                if supply_output != "e":
                    await message.channel.send(embed = supply_output)
                else:
                    await message.channel.send(embed = db.error())
            elif str_divide[0] == "tvl-ratio":
                warning = suggestSlash("`/tvl-ratio [coin]`")
                await message.channel.send(embed = warning)
                output = db.get_mcap_to_tvl_ratio(str_divide[1])
                correct_check = True
                await message.channel.send(embed = output)
            elif str_divide[0] == "tvl":
                warning = suggestSlash("`/tvl [coin]`")
                await message.channel.send(embed = warning)
                output = db.get_tvl(str_divide[1])
                correct_check = True
                await message.channel.send(embed = output)
            # if user's request has more than one string, send error
            elif len(str_divide) > 1:
                # ignores commands about coins
                for word in useless_words:
                    if str_divide[0] == word:
                        pass
                # else:
                #     await message.channel.send(embed = db.error())
            elif len(str_divide) == 1:
                # if user wants events
                # if command == "events":
                #     await message.channel.send(db.get_events())
                # elif command == 'global':
                #     get_global_data()
                # if user wants eth gas prices
                if command == "gas":
                    if not (str(message.guild) == "/r/Pennystocks" or str(message.guild) == "Playground"):
                        await message.channel.send(embed = db.gas())
                # if user wants to get the knowledge of shi's shitcoin
                elif command == "fetch":
                    await message.channel.send(last_fetch_time)
                elif command == "trendy":
                    await message.channel.send(embed = db.get_trending())
                    correct_check = True
                elif command == 'future':
                    await message.channel.send(db.future())
                    correct_check = True
                elif command == "crypto_gsb":
                    await message.channel.send("Running global sync!")
                    # bot_class.tree.copy_global_to()
                    return_val = await bot_class.tree.sync()
                    print(return_val)
                elif command == "rekt":
                    await message.channel.send(embed = db.get_rekt())
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
                # elif str_divide[0] == "servers":
                #     result = db.get_servers(bot)
                #     await message.channel.send(result)
                elif str_divide[0] == "crypto_some_trees":
                    print("ran command")
                    test_guilds= [769635647782256690, 297939923741310979]
                    for guild in test_guilds:
                        try:
                            # bot_class.tree.copy_global_to(guild = discord.Object(id = guild))
                            await bot_class.tree.sync(guild = discord.Object(id = guild))
                            print("Updated guild: ", guild)
                        except Exception as err:
                            print("Could not add guild: ", guild)
                else:
                    result = db.get_coin_price(command)
                    if result != "":
                        correct_check = True
                        await message.channel.send(embed = db.get_coin_price(command))
                        warning = suggestSlash("`/c [coin]`")
                        await message.channel.send(embed = warning)
            # else:
            #         await message.channel.send(embed = db.error())
            # if correct_check:
                # warning = suggestSlash()
                # await message.channel.send(embed = warning)
            return
    print("running bot" + str(datetime.datetime.now()) + bot_token)
    bot_class.run(bot_token)
