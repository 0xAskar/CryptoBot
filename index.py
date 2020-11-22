import ids
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
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import mplfinance as mpf

public_key = "50d8dbb3ff26eec310978d56a17705489eeee4882f65d7034019598998bc8ea6"
bot_token = ids.bot_token_real
guild_s = "Playground"
guild_p = "/r/Pennystocks"
load_dotenv()
cg = CoinGeckoAPI()
print(cg.ping())
bot = commands.Bot(command_prefix='!')
bot_name = ""
bot_member = None
bot_id = ids.bot_id_real

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
        price_data = cg.get_price(ids= coin_label, vs_currencies='usd', include_24hr_change='true', include_market_cap = 'true')
        price = price_data[coin_label]['usd']
        price = round(price,3)
        price = "{:,}".format(price)
        percent_change = price_data[coin_label]['usd_24h_change']
        percent_change = round(percent_change, 2)
        market_cap = price_data[coin_label]['usd_market_cap']
        market_cap = round(market_cap, 2)
        market_cap = check_large(market_cap)
        # market_cap = "{:,}".format(market_cap)
        coin_name = change_cap(coin_name)
        embedResponse = discord.Embed(title=coin_name + " Info", color=0xFF8C00)
        embedResponse.add_field(name="Price", value= "$" + str(price), inline=False)
        embedResponse.add_field(name="Percent Change (24hr)", value= str(percent_change) + "%", inline=False)
        embedResponse.add_field(name="Market Cap", value= "$" + market_cap, inline=False)
        response1 = "```" + coin_name + "'s price: $" + str(price) + "\n" + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
        # response2 = "```" + coin_name + "'s price: $" + str(price) + ", " + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
        return embedResponse
    return error()

def get_coin_chart(coin_name, num_days):
    coin_label = ""
    coin_name = coin_name.lower()
    coin_label = check_coin(coin_name)

    temp = str(num_days)
    if not temp.isdigit():
        temp = temp.lower()
        if temp != "max":
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
        #create strings for title
        percent_change = ((y_vals[len(y_vals) - 1] - y_vals[0]) / y_vals[0]) * 100
        percent_change = round(percent_change, 2)
        changed, days = "", ""
        if num_days == "1":
            days = "the past 24 hours"
        elif num_days == "MAX" or num_days == "max":
            days = "Within Lifetime"
        else:
            days = "Past " + num_days + " Days"
        # change title based on percent
        if percent_change > 0:
            changed = "+"
        else:
            changed = ""
        percent_change = "{:,}".format(percent_change) # had to do it here because this converts it to a string, need it as a int above
        coin_label = change_cap(coin_label)
        title1 = coin_label + " " + changed + percent_change + "% - " + days
        plt.title(title1)
        plt.xlabel('Days')
        plt.ylabel('Price - USD')
        plt.savefig('chart.png', edgecolor = 'black')
        return True
    else:
        return False

def get_candle_chart(coin_name, num_days):
    #coin label work
    coin_label = ""
    coin_name = coin_name.lower()
    coin_label = check_coin(coin_name)
    #checking if num days is valid
    valid_days = ["1","7","14","30","90","180","365", "MAX", "max"]
    check = False
    error_days = "```Command Error: Wrong number of days: Only can input '1','7','14','30','90','180','365','MAX'```"
    for day in valid_days:
        if num_days == day:
            check = True
    if check == False:
        return error_days

    if check_coin(coin_name) != "":
        candles = cg.get_coin_ohlc_by_id(id = coin_label, vs_currency='usd', days = num_days)
        plt.clf()
        date_arr, year, month, day, hour, open, high, low, close, volume = [], [], [], [], [], [], [], [], [], []
        dohlcv = [[]]
        count = 0
        time_conv = ""
        for point in candles:
            # convert to standard date and time, parse and add them into arrays
            if count == 0:
                time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
            # parse and add in the OHLC vectors
            open.append(point[1])
            high.append(point[2])
            low.append(point[3])
            close.append(point[4])
            volume.append(1)
            count += 1
        # create the date and dataframe
        period = len(open)
        dti = pd.date_range(time_conv, periods=period, freq='4H')
        ohlc = {"opens":open, "highs":high, "lows":low, "closes":close, "volumes":volume}
        ohlc = pd.DataFrame(data = ohlc, index = dti)
        ohlc.columns = ['Open', 'High', 'Low', 'Close', 'Volume'] #these two lines solved the dataframe problem
        ohlc.index.name = "Date"
        # plot and make it look good
        percent_change = ((close[len(close) - 1] - close[0]) / close[0]) * 100
        percent_change = round(percent_change, 2)
        changed, days = "", ""
        # change title based on days
        if num_days == "1":
            days = "the past 24 hours"
        elif num_days == "MAX" or num_days == "max":
            days = "Within Lifetime"
        else:
            days = "Past " + num_days + " Days"
        # change title based on percent
        if percent_change > 0:
            changed = "+"
        else:
            changed = ""

        percent_change = "{:,}".format(percent_change) # had to do it here because this converts it to a string, need it as a int above
        # title = "\n" + "\n" + coin_label + "'s price " + changed + percent_change + "% within " + days
        coin_label = change_cap(coin_label)
        title1 = "\n" + "\n" + coin_label + " " + changed + percent_change + "% - " + days
        mc = mpf.make_marketcolors(
                            up='tab:blue',down='tab:red',
                            wick={'up':'blue','down':'red'},
                            volume='tab:green',
                           )

        edited_style  = mpf.make_mpf_style(gridstyle = '-', facecolor = "lightgray", gridcolor = "white", edgecolor = "black", base_mpl_style = "classic", marketcolors=mc)
        mpf.plot(ohlc, type='candle', title = title1, figratio = (16,10), ylabel = 'Price - USD', style = edited_style, savefig = "candle.png")
        return ""
    else:
        return "error"


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

#find a better way of doing this instead of recopying the function
def change_cap(coin_name):
    coin_label = ""
    coin_name = coin_name.lower()
    for coin in cg.get_coins_list():
        if coin['id'] == coin_name or coin['symbol'] == coin_name:
            if coin['symbol'] == coin_name:
                coin_label = coin_name.upper()
            else:
                coin_label = coin_name.lower()
                coin_label = coin_label.capitalize()
            return coin_label
    return coin_label

def check_large(num): #there are better ways but atm, its not important
    letter = " M"
    num /= 1000000
    if (num >= 1000):
        letter = " B"
        num /= 1000
        if (num >= 1000):
            letter = " T"
            num /= 1000
    num = round(num, 1)
    return str(num) + letter

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
            "Candle Command: '!chart btc 5' <chart> <coin_name/symbol> <num days>, num days has to be one of these: '1','7','14','30','90','180','365','MAX'" + "\n" + \
            "Global Defi Stats: '!global_defi'" + "\n" + \
            "" + "\n" + \
            "Credits to CoinGecko® for the free API!```"
            await message.channel.send(response)
        elif chart_check == "chart":
            if len(str_divide) == 3:
                if get_coin_chart(str_divide[1], str_divide[2]):
                    embedImage = discord.Embed(color=0xFF8C00) #creates embed
                    embedImage.set_image(url="attachment://chart.png")
                    await message.channel.send(file = discord.File("chart.png"), embed = embedImage)
                    # await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            elif len(str_divide) == 2:
                if get_coin_chart(str_divide[1], 30):
                    embedImage = discord.Embed(color=0xFF8C00) #creates embed
                    embedImage.set_image(url="attachment://chart.png")
                    await message.channel.send(file = discord.File("chart.png"), embed = embedImage)
                    # await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            else:
                await message.channel.send(error())
                return
        elif str_divide[0] == "candle":
            if len(str_divide) == 3:
                candle_output = get_candle_chart(str_divide[1], str_divide[2])
                if candle_output == "":
                    embedImage = discord.Embed(color=0xFF8C00) #creates embed
                    embedImage.set_image(url="attachment://candle.png")
                    await message.channel.send(file = discord.File("candle.png"), embed = embedImage)
                    # await message.channel.send(file = discord.File('candle.png'))
                elif candle_output == "error":
                    await message.channel.send(error())
                else:
                    await message.channel.send(candle_output)
            elif len(str_divide) == 2:
                candle_output = get_candle_chart(str_divide[1], 30)
                if candle_output == "":
                    embedImage = discord.Embed(color=0xFF8C00) #creates embed
                    embedImage.set_image(url="attachment://candle.png")
                    await message.channel.send(file = discord.File("candle.png"), embed = embedImage)
                    # await message.channel.send(file = discord.File('candle.png'))
                elif candle_output == "error":
                    await message.channel.send(error())
                else:
                    await message.channel.send(candle_output)
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
                await message.channel.send(embed = get_coin_price(command))
        else:
                await message.channel.send(error())

bot.loop.create_task(background_task())
bot.run(bot_token)
