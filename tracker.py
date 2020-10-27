client_secret = "arlLaG80mW6GgG7cpQ7re_0zfbuZIqfI"
client_id = 769265839584051200
public_key = "50d8dbb3ff26eec310978d56a17705489eeee4882f65d7034019598998bc8ea6"
bot_token = 'NzY5MjY1ODM5NTg0MDUxMjAw.X5MgpA.NJQe7HIVJcdHyXuVH9S8NvUyWSM'
guild_s = "Playground"
# guild_penny = "Pennystocks"


cmc_key =  "98fa7239-19fd-4581-93e2-1bd68b544351"

# import all neccessary libraries
import os
import discord
import random
import asyncio
import requests
from dotenv import load_dotenv
from discord.ext import tasks, commands
from discord.ext.tasks import loop
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from discord.ext import commands

cmc = CoinMarketCapAPI(cmc_key)
ticker = "NONE"
load_dotenv()
bot = commands.Bot(command_prefix='!')
bot_name = ""
bot_member = None
bot_id = 769265839584051200

def bitcoin_output():
    m = cmc.cryptocurrency_listings_latest()
    price = m.data[0]['quote']['USD']['price']
    price = round(price,2)
    percent_change = m.data[0]['quote']['USD']['percent_change_24h']
    percent_change = round(percent_change, 2)
    response = "Bitcoin's price: $" + str(price) + ", Percent Change (24h): " + str(percent_change) + "%"
    return response

def ethereum_output():
    m = cmc.cryptocurrency_listings_latest()
    price = m.data[1]['quote']['USD']['price']
    percent_change = m.data[1]['quote']['USD']['percent_change_24h']
    percent_change = round(percent_change, 2)
    price = round(price,2)
    response = "Ethereum's price: $" + str(price) + ", Percent Change (24h): " + str(percent_change) + "%"
    return response

def btc_status():
    m = cmc.cryptocurrency_listings_latest()
    price = m.data[0]['quote']['USD']['price']
    price = round(price,2)
    response = "Bitcoin - $" + str(price)
    return response

def eth_status():
    m = cmc.cryptocurrency_listings_latest()
    price = m.data[1]['quote']['USD']['price']
    price = round(price,2)
    response = "Ethereum: $" + str(price)
    return response

async def background_task():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        if guild.name == guild_s:
            break
    for member in guild.members:
        if member.id == bot_id:
            bot_member = member
            bot_name = member.name
    while not bot.is_closed():
        await bot_member.edit(nick = btc_status())
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= eth_status()))
        await asyncio.sleep(300)

@bot.event
async def on_ready():
    # look for guild
    for guild in bot.guilds:
        if guild.name == guild_s:
            break
    # find members of guild
    members = '\n - '.join([member.name for member in guild.members])
    ids = [member.id for member in guild.members]
    for member in guild.members:
        if member.id == bot_id:
            bot_member = member
            bot_name = member.name

    # check that bot has connected to discord
    print(f'{bot_name} has connected to Discord!')


# function commands for checking bitcoins price
@bot.command(name = "bitcoin")
async def btc_price(message):
    await message.channel.send(bitcoin_output())
@bot.command(name = "btc")
async def btc_price(message):
    await message.channel.send(bitcoin_output())
@bot.command(name = "BTC")
async def btc_price(message):
    await message.channel.send(bitcoin_output())
@bot.command(name = "Bitcoin")
async def btc_price(message):
    await message.channel.send(bitcoin_output())

# function commands for checking ethereum price
@bot.command(name = "ethereum")
async def btc_price(message):
    await message.channel.send(ethereum_output())
@bot.command(name = "eth")
async def btc_price(message):
    await message.channel.send(ethereum_output())
@bot.command(name = "ETH")
async def btc_price(message):
    await message.channel.send(ethereum_output())
@bot.command(name = "Ethereum")
async def btc_price(message):
    await message.channel.send(ethereum_output())

bot.loop.create_task(background_task())
bot.run(bot_token) # runs forever

# @bot.event
# async def on_message(message):
#
#     link = "Here is the link to Trendy, do yourself a favor: https://www.youtube.com/channel/UCJpDaUsJ-IpvpDfH-AqZfcQ?view_as=subscriber"
#
#     info = message.content
#     info = info.lower()
#     if message.author == bot.user:
#         return
#
#     if info == "!link":
#         response = link
#         await message.channel.send(response)
#     elif info == "!bitcoin" or info == '!btc':
#         price = m.data[0]['quote']['USD']['price']
#         price = round(price,2)
#         percent_change = m.data[0]['quote']['USD']['percent_change_24h']
#         percent_change = round(percent_change, 2)
#         response = "Bitcoin's price: $" + str(price) + ", Percent Change: " + str(percent_change) + "%"
#         await message.channel.send(response)
#     elif info == "!ethereum" or info == '!eth':
#         price = m.data[1]['quote']['USD']['price']
#         percent_change = m.data[1]['quote']['USD']['percent_change_24h']
#         percent_change = round(percent_change, 2)
#         price = round(price,2)
#         response = "Ethereum's price: $" + str(price) + ", Percent Change: " + str(percent_change) + "%"
#         await message.channel.send(response)
