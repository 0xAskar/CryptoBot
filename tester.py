client_secret = "arlLaG80mW6GgG7cpQ7re_0zfbuZIqfI"
client_id = 769265839584051200
public_key = "50d8dbb3ff26eec310978d56a17705489eeee4882f65d7034019598998bc8ea6"
bot_token = "Nzc4ODMzNDczOTEzMjI1MjE2.X7XvMg.0uX-FaB5EZAKDBtn2VpWGQVr0xw"
guild_s = "Playground"
guild_p = "/r/Pennystocks"


import os
import discord
import random
import asyncio
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import tasks, commands
from discord.ext.tasks import loop
from pycoingecko import CoinGeckoAPI
from discord.ext import commands
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import mplfinance as mpf

load_dotenv()
cg = CoinGeckoAPI()
print(cg.ping())
bot = commands.Bot(command_prefix='!')
bot_name = ""
bot_member = None
bot_id = 778833473913225216

def btc_status():
    price_data = cg.get_price(ids= 'bitcoin', vs_currencies='usd')
    price = price_data['bitcoin']['usd']
    price = round(price,2)
    response = "Bitcoin - $" + str(price)
    return response

def eth_status():
    price_data = cg.get_price(ids= 'Ethereum', vs_currencies='usd')
    price = price_data['ethereum']['usd']
    price = round(price,2)
    response = "Ethereum: $" + str(price)
    return response

def get_coin_price(coin_name):
    coin_label = ""
    coin_name = coin_name.lower()
    coin_label = check_coin(coin_name)
    if check_coin(coin_name) != "":
        price_data = cg.get_price(ids= coin_label, vs_currencies='usd', include_24hr_change='true')
        price = price_data[coin_label]['usd']
        price = round(price,3)
        price = "{:,}".format(price)
        percent_change = price_data[coin_label]['usd_24h_change']
        percent_change = round(percent_change, 2)
        response = "```" + coin_name + "'s price: $" + str(price) + "\n" + "Percent Change (24h): " + str(percent_change) + "%```"
        return response
    return error()

def get_coin_chart(coin_name, num_days):
    coin_label = ""
    coin_name = coin_name.lower()
    coin_label = check_coin(coin_name)

    if num_days == 'MAX' or num_days == 'max':
        num_days = 100000

    else:
        temp = str(num_days)
        if not temp.isdigit():
            return False

    if check_coin(coin_name) != "":
        charts = cg.get_coin_market_chart_by_id(id = coin_label, vs_currency='usd', days = num_days)
        plt.clf()
        x_vals = []
        y_vals = []
        for point in charts['prices']:
            time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            x_vals.append(time_conv)
            y_vals.append(point[1])
        ax = plt.axes()
        plt.plot(x_vals, y_vals)
        # pyplot.locator_params(nbins=4)
        ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        # ax.set_xticklabels([label.replace(" ", "\n") for label in x_vals])
        plt.xlabel('Days')
        plt.ylabel('Price - USD')
        if num_days == 100000:
            num_days = 'MAX'
        plt.title(coin_label + "'s Price - Past " + str(num_days) + " days")
        plt.savefig('chart.png', edgecolor = 'black')
        return True
    else:
        return False

def get_candle_chart(coin_name, num_days):
    coin_label = ""
    coin_name = coin_name.lower()
    coin_label = check_coin(coin_name)

    if num_days == 'MAX' or num_days == 'max':
        num_days = 100000

    else:
        temp = str(num_days)
        if not temp.isdigit():
            return False

    if check_coin(coin_name) != "":
        candles = cg.get_coin_ohlc_by_id(id = coin_label, vs_currency='usd', days = 7)
        plt.clf()
        time = []
        open = []
        high = []
        low = []
        close = []
        volume = []
        for point in candles:
            # time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            # time_conv = datetime.fromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            time_conv = datetime.utcfromtimestamp(point[0]/1000).strftime("%B %d, %Y")
            time.append(time_conv)
            open.append(point[1])
            high.append(point[2])
            low.append(point[3])
            close.append(point[4])
            volume.append(1)
        date = pd.DatetimeIndex(time)
        ohlc = {'Date' : date, 'open':open, 'high':high, 'low':low, 'close':close, 'volume' : volume}
        data = pd.DataFrame(data = ohlc)
        mpf.plot(data, type='candle', style='charles', title='', ylabel='', ylabel_lower='',
        volume=False, mav=(3,6,9), savefig='chart.png')
        # # mpf.candlestick_ohlc(ax, ohlc.values, width = 0.6,
        # #          colorup = 'green', colordown = 'red',
        # #          alpha = 0.8)
        # data = pd.DataFrame(data = ohlc)
        # # ax = plt.axes()
        # mpf.plot(data, type = 'candle')
        # # pyplot.locator_params(nbins=4)
        # # ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        # # ax.set_xticklabels([label.replace(" ", "\n") for label in x_vals])
        # # mpf.xlabel('Days')
        # # plt.ylabel('Price - USD')
        # # if num_days == 100000:
        # #     num_days = 'MAX'
        # plt.title(coin_label + "'s Price - Past " + str(num_days) + " days")
        # plt.savefig('chart.png', edgecolor = 'black')
        return True
    else:
        return False


def check_coin(coin_name):
    coin_label = ""
    coin_name = coin_name.lower()
    for coin in cg.get_coins_list():
        if coin['id'] == coin_name or coin['symbol'] == coin_name:
            if coin['symbol'] == coin_name:
                coin_label = coin['id']
            else:
                coin_label = coin_name
            return coin_label
    return coin_label

def get_events():
    news = cg.get_events(country_code = 'US', type = "Eventf", page = 10, upcoming_events_only = False, from_date = "2019-01-01", to_date = "2020-10-02")
    return news['data']

def get_list_exchanges():
    ex = cg.get_exchanges_list()
    response = "```List of Exchanges: " + "\n"
    for i in range(len(ex)):
        response += ex[i]['id'] + ", "
    response += "```"
    return response

def get_global_data():
    print(cg.get_coins_markets(vs_currency = 'USD'))

def get_global_defi_data():
    coin_label = ""
    news = cg.get_global_decentralized_finance_defi()
    def_mc = news['defi_market_cap']
    def_mc = float(def_mc)
    def_mc = round(def_mc,2)
    def_mc = "{:,}".format(def_mc)
    response = "```Defi Market Cap: $" + str(def_mc) + "\n"
    der = news['defi_to_eth_ratio']
    der = float(der)
    der = round(der,2)
    response += "Defi To Eth Ratio: " + str(der) + "\n"
    defi_dom = news['defi_dominance']
    defi_dom = float(defi_dom)
    defi_dom = round(defi_dom,2)
    response += "Defi Dominance: " + str(defi_dom) + "%" + "\n"
    tdc = news['top_coin_name']
    tdcmc = news['top_coin_defi_dominance']
    tdcmc = float(tdcmc)
    tdcmc = round(tdcmc,2)
    response += "Top Defi Coin: " + tdc + "\n" + "Top Defi Coin Dominance: " + str(tdcmc) + "%"+ "\n```"
    return response

def future():
    response = "BAND is a shitcoin [I'm not changing this Shi]"
    return response

def error():
    response = "Not valid command/coin"
    return response

@bot.event
async def background_task():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        if guild.name == guild_p:
            break
    for member in guild.members:
        if member.id == bot_id:
            bot_member = member
            bot_name = member.name
    while not bot.is_closed():
        await bot_member.edit(nick = btc_status())
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= eth_status()))
        await asyncio.sleep(5)


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
    print(f'{bot_name} has connected to Discord!')

@bot.event
async def on_message(message):
    info = message.content
    command = ""
    chart_check = ""
    info = info.lower()
    if message.author == bot.user:
        return
    if info[0] == '!':
        if len(info) >= 6:
            chart_check = info[1:6]
        command = info[1:]
        str_divide = command.split()
        if command == "help-crypto":
            response = "```This bot gives sends live updates of " + \
            "any cryptocurrency" + "\n" + \
            "Commands:" + "\n" + \
            "Price Command: ![coin symbol/name], '!btc' or '!bitcoin'" + "\n" + \
            "Chart Command: '!chart btc 5' <chart> <coin_name/symbol> <num days>" + "\n" + \
            "Global Defi Stats: '!global_defi'" + "\n" + \
            "" + "\n" + \
            "Credits to CoinGecko® for the free API!```"
            await message.channel.send(response)
        elif chart_check == "chart":
            if len(str_divide) == 3:
                if get_coin_chart(str_divide[1], str_divide[2]):
                    await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            elif len(str_divide) == 2:
                if get_coin_chart(str_divide[1], 30):
                    await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            else:
                await message.channel.send(error())
                return
        elif str_divide[0] == "candle":
            if len(str_divide) == 3:
                if get_candle_chart(str_divide[1], str_divide[2]):
                    await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            elif len(str_divide) == 2:
                if get_candle_chart(str_divide[1], 30):
                    await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            else:
                await message.channel.send(error())
                return
        elif len(str_divide) > 1:
            if command == "future":
                pass
        elif len(str_divide) == 1:
            if command == "events":
                await message.channel.send(get_events())
            # elif command == 'global':
            #     get_global_data()
            elif command == 'future':
                await message.channel.send(future())
            elif command == 'global_defi':
                await message.channel.send(get_global_defi_data())
            elif command == 'list-exchanges':
                await message.channel.send(get_list_exchanges())
            else:
                await message.channel.send(get_coin_price(command))
        else:
                await message.channel.send(error())

bot.loop.create_task(background_task())
bot.run(bot_token)
