client_secret = "arlLaG80mW6GgG7cpQ7re_0zfbuZIqfI"
client_id = 769265839584051200
public_key = "50d8dbb3ff26eec310978d56a17705489eeee4882f65d7034019598998bc8ea6"
guild_s = "Playground"
# guild_penny = "Pennystocks"


# import all neccessary libraries
import os
import discord
import random
import asyncio
import requests
from dotenv import load_dotenv
from discord.ext import tasks, commands
import matplotlib.pyplot as plt
from discord.ext.tasks import loop
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from pycoingecko import CoinGeckoAPI
from discord.ext import commands

load_dotenv()
cg = CoinGeckoAPI()
bot = commands.Bot(command_prefix='!')
bot_name = ""
bot_member = None
bot_id = 769265839584051200

def btc_status():
    # cg = CoinGeckoAPI()
    price_data = cg.get_price(ids= 'bitcoin', vs_currencies='usd')
    price = price_data['bitcoin']['usd']
    price = round(price,2)
    response = "Bitcoin - $" + str(price)
    return response

def eth_status():
    # cg = CoinGeckoAPI()
    price_data = cg.get_price(ids= 'ethereum', vs_currencies='usd')
    price = price_data['ethereum']['usd']
    price = round(price,2)
    response = "Ethereum: $" + str(price)
    return response

def get_coin_price(coin_name):
    coin_name = coin_name.lower()
    # cg = CoinGeckoAPI()
    coin_label = coin_name
    for coin in cg.get_coins_list():
        if coin['id'] == coin_name or coin['symbol'] == coin_name:
            if coin['symbol'] == coin_name:
                coin_label = coin['id']
            price_data = cg.get_price(ids= coin_label, vs_currencies='usd', include_24hr_change='true')
            price = price_data[coin_label]['usd']
            price = round(price,2)
            percent_change = price_data[coin_label]['usd_24h_change']
            percent_change = round(percent_change, 2)
            response = coin_name + "'s price: $" + str(price) + ", Percent Change (24h): " + str(percent_change) + "%"
            return response
    response = "Not valid command/coin"
    return response

def get_coin_chart(coin_name):



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
        await asyncio.sleep(10)

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
    charts = cg.get_coin_market_chart_by_id(id = 'bitcoin', vs_currency='usd', days = 5)
    x_vals = []
    y_vals = []
    for point in charts['prices']:
        x_vals.append(point[0])
        y_vals.append(point[1])
    plt.plot(x_vals, y_vals)
    plt.xlabel('days')
    plt.ylabel('price')
    plt.title('Bitcoin Price - 5 days')
    plt.show()
    # check that bot has connected to discord
    print(f'{bot_name} has connected to Discord!')


# function commands for checking bitcoins price

@bot.event
async def on_message(message):
    link = "Here is the link to Trendy, do yourself a favor: https://www.youtube.com/channel/UCJpDaUsJ-IpvpDfH-AqZfcQ?view_as=subscriber"

    info = message.content
    command = ""
    info = info.lower()
    if message.author == bot.user:
        return
    if info[0] == '!':
        command = info[1:]
        if command == "help":
            response = "This bot gives sends live updates of " + \
            "any cryptocurrency that is available on CoinGecko®." + "\n" + \
            "Example commands: '!btc' or '!bitcoin'" + "\n" + \
            "Credits to CoinGecko® for the free API!"
            await message.channel.send(response)
        else:
            await message.channel.send(get_coin_price(command))

bot.loop.create_task(background_task())
bot.run(bot_token) # runs forever
