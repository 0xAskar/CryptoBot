import bot_ids
import bot_class
from bot_class import discord_bot
from dotenv import load_dotenv
import asyncio
import discord
from discord.ext import tasks, commands
from discord.ext.tasks import loop
from discord.ext import commands

# global variables
bot_token = bot_ids.bot_token_real
guild_s = "Playground"
guild_p = "/r/Pennystocks"
bot_id = bot_ids.bot_id_real
askar_id = 372010870756081675
bot_name = ""
bot_member = None
askar_member = None
askar_name = ""


if __name__ == "__main__":
    # load up the coingecko, etherscan, and discord api's
    load_dotenv()

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='!', intents = intents)

    db = discord_bot()
    print(db.cg.ping())
    # main functions that need to run

    @bot.event
    async def background_task():
        await bot.wait_until_ready()
        for guild in bot.guilds:
            if guild.name == guild_p:
                break
        # intents = discord.intents.all()
        # client = discord.Client(intent = intents)
        for member in guild.members:
            if member.id == bot_id:
                bot_member = member
                bot_name = member.name
            if member.id == askar_id:
                askar_member = member
                askar_name = member.name
        while not bot.is_closed():
            await bot_member.edit(nick = db.btc_status())
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= db.eth_status()))
            await asyncio.sleep(10)


    @bot.event
    async def on_ready():
        for guild in bot.guilds:
            if guild.name == guild_p:
                break
        members = '\n - '.join([member.name for member in guild.members])
        ids = [member.id for member in guild.members]
        for member in guild.members:
            if member.id == bot_id:
                bot_member = member
                bot_name = member.name
            if member.id == askar_id:
                askar_member = member
                askar_name = member.name
        print(f'{bot_name} has connected to Discord!')

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
        if info[0] == '!':
            #  parse out "!", and separate into string array
            command = info[1:]
            str_divide = command.split()
            # if user asks for help on commands
            if command == "crypto-help":
                response = "```CryptoBot gives you sends live updates of " + \
                "any cryptocurrency!" + "\n" + "\n" + \
                "Commands:" + "\n" + "\n" + \
                "   Price Command: ![coin symbol/name], '!btc' or '!bitcoin' - retreive price information about a coin" + "\n" + "\n" + \
                "   Chart Command: '!chart btc 5' <chart> <coin> <num days> - retreive the line chart of a coin" + "\n" + "\n" + \
                "   Candle Command: '!chart btc 5' <chart> <coin_name/symbol> <num days>, "\
                "days has to be one of these:" + "\n" + "   '1','7','14','30','90','180','365','MAX' - retreive the candle chart of a coin" + "\n" + "\n" + \
                "   Suggestion Command: !suggestion do this' <suggestion> <message> - send a suggestion for the bot" + "\n" + "\n" + \
                "   Gas Command: '!gas' - get information about gwei prices" + "\n" + "\n" + \
                "   Global Defi Stats: '!global_defi' - get global information about defi" + "\n" + "\n" + \
                "Credits to CoinGecko® for the free API!```"
                suggester = db.find_member(bot, guild_p, message.author.id)
                await suggester.send(response)
                await message.add_reaction('\N{THUMBS UP SIGN}')
            # if user wants to send a suggestion
            elif str_divide[0] == "suggestion":
                if len(str_divide) > 1:
                    user = db.find_member(bot, guild_p, askar_id)
                    suggester = db.find_member(bot, guild_p, message.author.id)
                    await user.send("suggestion" + " by " + suggester.name + ": " + command[11:])
                    await message.channel.send("```Your suggestion was sent```")
                else:
                    await message.channel.send("```Invalid Suggestion: There was no suggestion```")
            # if user requests a line chart of a coin
            elif str_divide[0] == "chart":
                if len(str_divide) == 3:
                    if db.get_coin_chart(str_divide[1], str_divide[2]):
                        await message.channel.send(file = discord.File('chart.png'))
                    else:
                        await message.channel.send(db.error())
                # if user doesn't specify num days, default to 30
                elif len(str_divide) == 2:
                    if db.get_coin_chart(str_divide[1], "30"):
                        await message.channel.send(file = discord.File('chart.png'))
                    else:
                        await message.channel.send(db.error())
                else:
                    await message.channel.send(db.error())
                    return
            # if user requests candle chart of a coin
            elif str_divide[0] == "candle":
                if len(str_divide) == 3:
                    candle_output = db.get_candle_chart(str_divide[1], str_divide[2])
                    if candle_output == "":
                        embedImage = discord.Embed(color=0xFF8C00) #creates embed
                        embedImage.set_image(url="attachment://candle.png")
                        await message.channel.send(file = discord.File("candle.png"), embed = embedImage)
                    elif candle_output == "error":
                        await message.channel.send(db.error())
                    else:
                        await message.channel.send(candle_output)
                # if user doesn't specify num days, default to 30
                elif len(str_divide) == 2:
                    candle_output = db.get_candle_chart(str_divide[1], "30")
                    if candle_output == "":
                        await message.channel.send(file = discord.File('candle.png'))
                    elif candle_output == "error":
                        await message.channel.send(db.error())
                    else:
                        await message.channel.send(candle_output)
                else:
                    await message.channel.send(db.error())
            # if user's request has more than one string, send error
            elif len(str_divide) > 1:
                # ignores commands about coins
                if command == "future":
                    pass
                else:
                    await message.channel.send(db.error())
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
                elif command == 'future':
                    await message.channel.send(db.future())
                # if user wants info about global defi stats
                elif command == 'global_defi':
                    await message.channel.send(db.get_global_defi_data())
                # if user wants info about exchanges
                elif command == 'list-exchanges':
                    await message.channel.send(db.get_list_exchanges())
                # if user wants info about any coin
                else:
                    result = db.get_coin_price(command)
                    if result == "":
                        await message.channel.send(db.error())
                    else:
                        await message.channel.send(embed = db.get_coin_price(command))
            else:
                    await message.channel.send(db.error())

    # run background task and bot indefintely
    bot.loop.create_task(background_task())
    bot.run(bot_token)
