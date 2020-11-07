client_secret = "arlLaG80mW6GgG7cpQ7re_0zfbuZIqfI"
client_id = 769265839584051200
public_key = "50d8dbb3ff26eec310978d56a17705489eeee4882f65d7034019598998bc8ea6"
bot_token = "NzY5MjY1ODM5NTg0MDUxMjAw.X5MgpA.OUD54A-Q90g8uLnaaEFVbGT3Ooc"
guild_s = "Playground"
# guild_penny = "Pennystocks"


# import all neccessary libraries
import os
import discord
import random
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import tasks, commands
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from discord.ext.tasks import loop
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from pycoingecko import CoinGeckoAPI
from discord.ext import commands

load_dotenv()
cg = CoinGeckoAPI()
print(cg.ping())
bot = commands.Bot(command_prefix='!')
coin_label = ""
bot_name = ""
bot_member = None
bot_id = 769265839584051200

def btc_status():
    price_data = cg.get_price(ids= 'bitcoin', vs_currencies='usd')
    price = price_data['bitcoin']['usd']
    price = round(price,2)
    response = "Bitcoin - $" + str(price)
    return response

def eth_status():

    # very weird bug, randoly stopped working for id: ethereum had to use Ethereum

    price_data = cg.get_price(ids= 'Ethereum', vs_currencies='usd')
    price = price_data['ethereum']['usd']
    price = round(price,2)
    response = "Ethereum: $" + str(price)
    return response

def get_coin_price(coin_name):
    coin_name = coin_name.lower()
    coin_label = check_coin(coin_name)
    if check_coin(coin_name) != "":
        price_data = cg.get_price(ids= coin_label, vs_currencies='usd', include_24hr_change='true')
        price = price_data[coin_label]['usd']
        price = round(price,2)
        price = "{:,}".format(price)
        percent_change = price_data[coin_label]['usd_24h_change']
        percent_change = round(percent_change, 2)
        # response = coin_name + "'s price:** $" + str(price) + ", **Percent Change (24h): **" + str(percent_change) + "%"
        # response = coin_name + "'s price: **$" + price + "**" + ", Percent Change (24h): " + "**" + percent_change + "%**"
        response = "```" + coin_name + "'s price: $" + str(price) + "\n" + "Percent Change (24h): " + str(percent_change) + "%```"
        return response
    return error()

def get_coin_chart(coin_name, num_days):
    coin_name = coin_name.lower()
    coin_label = check_coin(coin_name)

    # check if num_days is MAX
    if num_days == 'MAX' or num_days == 'max':
        num_days = 100000

    # fix bug for

    # check if num_days is a number
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
            # time_conv = time_conv.split()
            x_vals.append(time_conv)
            y_vals.append(point[1])
        ax = plt.axes()
        plt.plot(x_vals, y_vals)
        ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        ax.set_xticklabels([label.replace(" ", "\n") for label in x_vals])
        # x_vals_shorten = []
        # for label in x_vals:
        #     temp = label.split()
        #     # x_vals_shorten.append(temp[0])
        # for i in x_vals_shorten:
        #     ax.set_xticklabels(i)
        # plt.xticks(rotation=45)
        plt.xlabel('Days')
        plt.ylabel('Price - USD')
        if num_days == 100000:
            num_days = 'MAX'
        plt.title(coin_label + "'s Price - Past " + str(num_days) + " days")
        plt.savefig('chart.png', edgecolor = 'black')
        return True
    else:
        return False

def check_coin(coin_name):
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
    # get the defi gloabl data
    news = cg.get_global_decentralized_finance_defi()
    # get the defi market cap
    def_mc = news['defi_market_cap']
    def_mc = float(def_mc)
    def_mc = round(def_mc,2)
    def_mc = "{:,}".format(def_mc)
    response = "```Defi Market Cap: $" + str(def_mc) + "\n"
    # response = "Defi Market Cap: $ " + "**" + str(def_mc) + "**" + "\n"
    # get the defi - to - eth ratio
    der = news['defi_to_eth_ratio']
    der = float(der)
    der = round(der,2)
    # response += "Defi To Eth Ratio: " + "**" + str(der) + "**" + "\n"
    response += "Defi To Eth Ratio: " + str(der) + "\n"
    # get the defi dominance
    defi_dom = news['defi_dominance']
    defi_dom = float(defi_dom)
    defi_dom = round(defi_dom,2)
    # response += "Defi Dominance: " + "**" + str(defi_dom) + "%**" + "\n"
    response += "Defi Dominance: " + str(defi_dom) + "%" + "\n"
    # top defi coin and its market cap
    tdc = news['top_coin_name']
    tdcmc = news['top_coin_defi_dominance']
    tdcmc = float(tdcmc)
    tdcmc = round(tdcmc,2)
    # response += "Top Defi Coin: " + "**" + tdc + "**" + "\n" + "Top Defi Coin Dominance: " + "**" + str(tdcmc) + "%**"+ "\n```"
    response += "Top Defi Coin: " + tdc + "\n" + "Top Defi Coin Dominance: " + str(tdcmc) + "%"+ "\n```"
    return response


def error():
    response = "Not valid command/coin"
    return response

@bot.event
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
        await asyncio.sleep(5)


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
    # print(cg.get_events_types())
    # print(cg.get_events(country_code = 'US', event = 'Event', page = 10, upcoming_events_only = False))
    # cmc = cg.get_global()
    # for i in cmc['total_market_cap']:
    #     print(cmc['total_market_cap'][i])
    # print(cg.get_coin_by_id(id = 'bitcoin'))
    # ex = cg.get_exchanges_list()
    # for i in range(len(ex)):
    #     print(ex[i]['id'])
    # print(cg.get_exchanges_status_updates_by_id(id = 'binance'))


# function commands for checking bitcoins price

@bot.event
async def on_message(message):
    # create some variables
    info = message.content
    command = ""
    chart_check = ""
    info = info.lower()
    # check if a bot sent the message, if so, don't respond
    if message.author == bot.user:
        return
    #check if it is a command
    if info[0] == '!':
        #check if the word qualifies to be a chart command
        if len(info) >= 6:
            chart_check = info[1:6]
        command = info[1:]
        str_divide = info.split()
        if command == "help":
            response = "This bot gives sends live updates of " + \
            "any cryptocurrency that is available on CoinGecko®." + "\n" + \
            "Example commands for price: '!btc' or '!bitcoin'" + "\n" + \
            "Example commands for chart: '!chart btc 5'" + "\n" + \
            "The number refers to the number of days or you can specify 'max' or 'MAX'" + "\n" + \
            "Credits to CoinGecko® for the free API!"
            await message.channel.send(response)
        elif chart_check == "chart":
            # asking for chart and specify days
            if len(str_divide) == 3:
                if get_coin_chart(str_divide[1], str_divide[2]):
                    await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            # asking for chart and doesn't specify days
            elif len(str_divide) == 2:
                if get_coin_chart(str_divide[1], 30):
                    await message.channel.send(file = discord.File('chart.png'))
                else:
                    await message.channel.send(error())
            else:
                await message.channel.send(error())
                return
        elif len(str_divide) == 1:
            if command == "events":
                await message.channel.send(get_events())
            elif command == 'global':
                get_global_data()
                # await message.channel.send(get_global_data())
            elif command == 'global_defi':
                await message.channel.send(get_global_defi_data())
            elif command == 'list-exchanges':
                await message.channel.send(get_list_exchanges())
            else:
                await message.channel.send(get_coin_price(command))
        else:
            await message.channel.send(error())

bot.loop.create_task(background_task())
bot.run(bot_token) # runs forever
