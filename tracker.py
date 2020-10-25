client_secret = "arlLaG80mW6GgG7cpQ7re_0zfbuZIqfI"
client_id = 769265839584051200
public_key = "50d8dbb3ff26eec310978d56a17705489eeee4882f65d7034019598998bc8ea6"
bot_token = 'NzY5MjY1ODM5NTg0MDUxMjAw.X5MgpA.NJQe7HIVJcdHyXuVH9S8NvUyWSM'
guild = "Playground"


cmc_key =  "98fa7239-19fd-4581-93e2-1bd68b544351"

# import all neccessary libraries
import os
import discord
import random
import requests
from dotenv import load_dotenv
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import sys
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from discord.ext import commands

cmc = CoinMarketCapAPI(cmc_key)
m = cmc.cryptocurrency_listings_latest()
ticker = "NONE"
load_dotenv()
bot = commands.Bot(command_prefix='!')
# Token = os.getenv('DISCORD_TOKEN')
# print(Token)

# establish client connection to discord api

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

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

def bitcoin_output():
    price = m.data[0]['quote']['USD']['price']
    price = round(price,2)
    percent_change = m.data[0]['quote']['USD']['percent_change_24h']
    percent_change = round(percent_change, 2)
    response = "Bitcoin's price: $" + str(price) + ", Percent Change: " + str(percent_change) + "%"
    return response
    
def ethereum_output():
    price = m.data[1]['quote']['USD']['price']
    percent_change = m.data[1]['quote']['USD']['percent_change_24h']
    percent_change = round(percent_change, 2)
    price = round(price,2)
    response = "Ethereum's price: $" + str(price) + ", Percent Change: " + str(percent_change) + "%"
    return reponse

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

@bot.command(name = "ethereum")
async def btc_price(message):
    await message.channel.send(bitcoin_output())
@bot.command(name = "eth")
async def btc_price(message):
    await message.channel.send(bitcoin_output())
@bot.command(name = "ETH")
async def btc_price(message):
    await message.channel.send(bitcoin_output())
@bot.command(name = "Ethereum")
async def btc_price(message):
    await message.channel.send(bitcoin_output())

bot.run(bot_token) # runs forever
