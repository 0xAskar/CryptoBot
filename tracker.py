client_secret = "arlLaG80mW6GgG7cpQ7re_0zfbuZIqfI"
client_id = 769265839584051200
public_key = "50d8dbb3ff26eec310978d56a17705489eeee4882f65d7034019598998bc8ea6"
bot_token = 'NzY5MjY1ODM5NTg0MDUxMjAw.X5MgpA.koCz6kt4uLFonz80eZdmEllarQ0'
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


cmc = CoinMarketCapAPI(cmc_key)
m = cmc.cryptocurrency_listings_latest()
ticker = "NONE"
load_dotenv()
# Token = os.getenv('DISCORD_TOKEN')
# print(Token)

# establish client connection to discord api
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):

    link = "Here is the link to Trendy, do yourself a favor: https://www.youtube.com/channel/UCJpDaUsJ-IpvpDfH-AqZfcQ?view_as=subscriber"

    info = message.content
    info = info.lower()
    if message.author == client.user:
        return

    if info == "!link":
        response = link
        await message.channel.send(response)
    elif info == "!bitcoin" or info == '!btc':
        price = m.data[0]['quote']['USD']['price']
        percent_change = m.data[0]['quote']['USD']['percent_change_24h']
        percent_change = round(percent_change, 2)
        price = round(price,2)
        response = "Bitcoin's price: $" + str(price) + ", Percent Change: " + str(percent_change) + "%"
        await message.channel.send(response)
    elif info == "!ethereum" or info == '!eth':
        price = m.data[1]['quote']['USD']['price']
        percent_change = m.data[1]['quote']['USD']['percent_change_24h']
        percent_change = round(percent_change, 2)
        price = round(price,2)
        response = "Ethereum's price: $" + str(price) + ", Percent Change: " + str(percent_change) + "%"
        await message.channel.send(response)

client.run(bot_token) # runs forever
