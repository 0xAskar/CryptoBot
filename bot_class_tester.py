import math
from math import log10, floor
import requests
import pandas as pd
import discord
from datetime import datetime
from discord.ext import tasks, commands
from discord.ext.tasks import loop
from discord.ext import commands
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import mplfinance as mpf
from pycoingecko import CoinGeckoAPI
import etherscan

class discord_bot:
    # api instance
    cg = CoinGeckoAPI()
    es = etherscan.Client(
        api_key='Y9KQMISGCXVNMJJXA2TBFMENF1JM2D4HAP',
        cache_expire_after=5,
    )

    # functions to gather btc, eth, and any coins price
    def btc_status(self):
        price_data = self.cg.get_price(ids= 'bitcoin', vs_currencies='usd')
        price = price_data['bitcoin']['usd']
        price = round(price,2)
        response = "Bitcoin - $" + str(price)
        return response

    def eth_status(self):
        price_data = self.cg.get_price(ids= 'Ethereum', vs_currencies='usd')
        price = price_data['ethereum']['usd']
        price = round(price,2)
        response = "Ethereum: $" + str(price)
        return response

    def get_coin_price(self, coin_name):
        coin_label = ""
        coin_name = coin_name.lower()
        coin_label = self.check_coin(coin_name)
        if self.check_coin(coin_name) != "":
            price_data = self.cg.get_price(ids= coin_label, vs_currencies='usd', include_24hr_change='true', include_market_cap = 'true')
            price = price_data[coin_label]['usd']
            price = round(price,3)
            price = "{:,}".format(price)
            percent_change = price_data[coin_label]['usd_24h_change']
            percent_change = round(percent_change, 2)
            market_cap = price_data[coin_label]['usd_market_cap']
            market_cap = round(market_cap, 2)
            market_cap = self.check_large(market_cap)
            mc = market_cap
            # market_cap = "{:,}".format(market_cap)
            coin_name = self.change_cap(coin_name)
            # embedResponse = discord.Embed(title=coin_name + " Info", color=0xFF8C00)
            embedResponse = discord.Embed(color=0xFF8C00)
            embedResponse.add_field(name= coin_name + " Price", value= "$" + str(price), inline=False)
            embedResponse.add_field(name= coin_name + " Percent Change (24hr)", value= str(percent_change) + "%", inline=False)
            embedResponse.add_field(name= coin_name + " Market Cap", value= "$" + mc, inline=False)
            response1 = "```" + coin_name + "'s price: $" + str(price) + "\n" + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
            # response2 = "```" + coin_name + "'s price: $" + str(price) + ", " + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
            return embedResponse
        return ""

    # retreive data and create candle chart of any coin
    def get_line_chart(self, coin_name, num_days):
        #coin label work
        coin_label = ""
        coin_name = coin_name.lower()
        coin_label = self.check_coin(coin_name)
        #checking if num days is valid
        temp = str(num_days)
        if not temp.isdigit():
            temp = temp.lower()
            if temp != "max":
                return False

        if self.check_coin(coin_name) != "":
            charts = self.cg.get_coin_market_chart_by_id(id = coin_label, vs_currency='usd', days = num_days)
            plt.clf()
            x_vals = []
            y_vals = []
            count = 0
            open, close, high, low, volume = [], [], [], [], []
            for point in charts['prices']:
                if count == 0:
                    time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
                x_vals.append(time_conv)
                y_vals.append(point[1])
                volume.append(1)
                count += 1
            # create the date and dataframe
            open = y_vals
            close = y_vals
            high = y_vals
            low = y_vals
            period = len(open)
            frequency = ""
            if num_days == "1":
                frequency = "5min"
            elif num_days != "max" and (int(num_days) <= 90 and int(num_days) > 1):
                frequency = "1H"
            else:
                frequency = "4D"
            dti = pd.date_range(time_conv, periods=period, freq=frequency)
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
            coin_label = self.change_cap(coin_label)
            title1 = "\n" + "\n" + coin_label + " " + changed + percent_change + "% - " + days
            mc = mpf.make_marketcolors(
                                up='tab:blue',down='tab:red',
                                wick={'up':'blue','down':'red'},
                                volume='tab:green',
                               )

            edited_style  = mpf.make_mpf_style(gridstyle = '-', facecolor = "lightgray", gridcolor = "white", edgecolor = "black", base_mpl_style = "classic", marketcolors=mc)
            mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = 'Price - USD', style = edited_style, savefig = "chart.png")
            return ""
        else:
            return "error"

    # chart of two coins for instance link/btc
    def get_line_chart_two(self, coin_name, coin_name2, num_days):
        #coin label work
        coin_label = ""
        coin_label2 = ""
        coin_name = coin_name.lower()
        coin_label2 = coin_name2.lower()
        coin_label = self.check_coin(coin_name)
        coin_label2 = self.check_coin(coin_name2)
        #checking if num days is valid
        temp = str(num_days)
        if not temp.isdigit():
            temp = temp.lower()
            if temp != "max":
                return False

        if self.check_coin(coin_name) != "":
            charts = self.cg.get_coin_market_chart_by_id(id = coin_label, vs_currency='usd', days = num_days)
            charts2 = self.cg.get_coin_market_chart_by_id(id = coin_label2, vs_currency = 'usd', days = num_days)
            plt.clf()
            x_vals = []
            y_vals = []
            count = 0
            open, close, high, low, volume = [], [], [], [], []
            min = len(charts["prices"])
            if min > len(charts2["prices"]):
                min = len(charts2["prices"])
            for point in charts['prices']:
                if count == min:
                    break
                if count == 0:
                    time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
                x_vals.append(time_conv)
                y_vals.append(point[1])
                volume.append(1)
                count += 1
            count = 0
            for point in charts2['prices']:
                if count == min:
                    break
                y_vals[count] = y_vals[count] / point[1]
                count += 1
            # create the date and dataframe
            open = y_vals
            close = y_vals
            high = y_vals
            low = y_vals
            period = len(open)
            frequency = ""
            if num_days == "1":
                frequency = "5min"
            elif num_days != "max" and (int(num_days) <= 90 and int(num_days) > 1):
                frequency = "1H"
            else:
                frequency = "4D"
            dti = pd.date_range(time_conv, periods=period, freq=frequency)
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
            coin_label = self.change_cap(coin_name.lower())
            coin_label2 = self.change_cap(coin_name2.lower())
            title1 = "\n" + "\n" + coin_label + "/" + coin_label2 + " " + changed + percent_change + "% - " + days
            mc = mpf.make_marketcolors(
                                up='tab:blue',down='tab:red',
                                wick={'up':'blue','down':'red'},
                                volume='tab:green',
                               )

            edited_style  = mpf.make_mpf_style(gridstyle = '-', facecolor = "lightgray", gridcolor = "white", edgecolor = "black", base_mpl_style = "classic", marketcolors=mc)
            mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = coin_label + "/" + coin_label2, style = edited_style, savefig = "chart.png")
            return ""
        else:
            return "error"


    # retreive data and create candle chart of any coin
    def get_candle_chart(self, coin_name, num_days):

        # used the below links for the mpf libraries
        # https://github.com/matplotlib/mplfinance#usage
        # https://github.com/matplotlib/mplfinance/blob/master/examples/styles.ipynb

        #coin label work
        coin_label = ""
        coin_name = coin_name.lower()
        coin_label = self.check_coin(coin_name)
        #checking if num days is valid
        valid_days = ["1","7","14","30","90","180","365", "MAX", "max"]
        check = False
        error_days = "```Command Error: Wrong number of days: Only can input '1','7','14','30','90','180','365','MAX'```"
        for day in valid_days:
            if num_days == day:
                check = True
        if check == False:
            return error_days

        if self.check_coin(coin_name) != "":
            candles = self.cg.get_coin_ohlc_by_id(id = coin_label, vs_currency='usd', days = num_days)
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
            frequency = ""
            if num_days == "1":
                frequency = "30min"
            elif num_days == "7" or num_days == "14" or num_days == "30":
                frequency = "4H"
            else:
                frequency = "4D"
            dti = pd.date_range(time_conv, periods=period, freq=frequency)
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
            coin_label = self.change_cap(coin_label)
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

    def get_conversion(self, num, first, second):
        first_coin = ""
        second_coin = ""
        first_coin = self.check_coin(first)
        second_coin = self.check_coin(second)
        # check if the coin names are valid
        if first_coin == "" or second_coin == "":
            return "e"
        # retreive price data about the coins
        first_data = self.cg.get_price(ids= first_coin, vs_currencies='usd')
        first_price = first_data[first_coin]['usd']
        second_data = self.cg.get_price(ids= second_coin, vs_currencies='usd')
        second_price = second_data[second_coin]['usd']
        # convert to proper cap.
        first = self.change_cap(first)
        second = self.change_cap(second)
        conv_num = float(num) * (first_price / second_price)
        conversion = self.round_num(conv_num)
        conversion = self.check_large(conversion)
        num = self.check_large(int(num))
        embedResponse = discord.Embed(color=0x7A2F8F)
        embedResponse.add_field(name= first + " to " + second + " Conversion", value= str(num) + " " + first + " = " + str(conversion) + " " + second, inline=False)
        return embedResponse

    # functions to check coins, names, and size

    # round numbers correctly, sig figs for <1, rounding for >1
    def round_num(self, num):
        if num < 1:
            num = round(num, -int(floor(log10(abs(num)))))
            temp = num
            count = 0
            while temp < 1:
                temp *= 10
                count += 1
            format_string = "{:." + str(count) + "f}"
            num = format_string.format(float(str(num)))
            return num
        else:
            return round(num, 2)

    def check_coin(self, coin_name):
        coin_label = ""
        coin_name = coin_name.lower()
        for coin in self.cg.get_coins_list():
            if coin['id'] == coin_name or coin['symbol'] == coin_name:
                if coin['symbol'] == coin_name:
                    coin_label = coin['id']
                else:
                    coin_label = coin_name
                return coin_label
        return coin_label

    #find a better way of doing this instead of recopying the function
    def change_cap(self, coin_name):
        coin_label = ""
        coin_name = coin_name.lower()
        for coin in self.cg.get_coins_list():
            if coin['id'] == coin_name or coin['symbol'] == coin_name:
                if coin['symbol'] == coin_name:
                    coin_label = coin_name.upper()
                else:
                    coin_label = coin_name.lower()
                    coin_label = coin_label.capitalize()
                return coin_label
        return coin_label

    def check_large(self, num): #there are better ways but atm, its not important
        letter = ""
        num = float(num)
        if num == 0:
            return "Not Found"
        if num >= 1000000:
            letter = " M"
            num /= 1000000
            if (num >= 1000):
                letter = " B"
                num /= 1000
                if (num >= 1000):
                    letter = " T"
                    num /= 1000
        num = round(num, 2)
        if letter == "":
            num = "{:,}".format(num)
        return str(num) + letter

    def get_events(self):
        news = self.cg.get_events(country_code = 'US', type = "Eventf", page = 10, upcoming_events_only = False, from_date = "2019-01-01", to_date = "2020-10-02")
        return news['data']

    def get_list_exchanges(self):
        ex = self.cg.get_exchanges_list()
        response = "```List of Exchanges: " + "\n"
        for i in range(len(ex)):
            response += ex[i]['id'] + ", "
        response += "```"
        return response

    def get_global_data(self):
        print(self.cg.get_coins_markets(vs_currency = 'USD'))

    def get_global_defi_data(self):
        coin_label = ""
        news = self.cg.get_global_decentralized_finance_defi()
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

    def gas(self):
        wei = self.es.get_gas_price()
        gwei = wei / 1000000000
        gwei = round(gwei, 2)
        avg_gas = 21000
        price_data = self.cg.get_price(ids= "ethereum", vs_currencies='usd')
        eth_price = price_data["ethereum"]['usd']
        eth_price = round(eth_price,3)
        usd_amount = (avg_gas * gwei / 1000000000) * eth_price
        usd_amount = round(usd_amount, 2)
        embedResponse = discord.Embed(title="Gas Price", color=0x0000ff)
        embedResponse.add_field(name="Gwei Price", value = str(gwei), inline=False)
        embedResponse.add_field(name="USD Price (avg trxn)", value= "$" + str(usd_amount), inline=False)
        return embedResponse

    def future(self):
        response = "BAND is a shitcoin [I'm not changing this Shi]"
        return response

    def error(self):
        response = "Not a valid command/coin"
        return response

    def find_member(self, bot, gld, mem_id):
        found_mem = None
        for guild in bot.guilds:
            if guild.name == gld:
                break
        members = '\n - '.join([member.name for member in guild.members])
        ids = [member.id for member in guild.members]
        for member in guild.members:
            if member.id == mem_id:
                return member

    # # retreive data and create line chart of any coin
    # def get_coin_chart(self, coin_name, num_days):
    #     coin_label = ""
    #     coin_name = coin_name.lower()
    #     coin_label = self.check_coin(coin_name)
    #
    #     temp = str(num_days)
    #     if not temp.isdigit():
    #         temp = temp.lower()
    #         if temp != "max":
    #             return False
    #
    #     if self.check_coin(coin_name) != "":
    #         charts = self.cg.get_coin_market_chart_by_id(id = coin_label, vs_currency='usd', days = num_days)
    #         plt.clf()
    #         x_vals = []
    #         y_vals = []
    #         for point in charts['prices']:
    #             time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
    #             x_vals.append(time_conv)
    #             y_vals.append(point[1])
    #         ax = plt.axes()
    #         plt.plot(x_vals, y_vals)
    #         # pyplot.locator_params(nbins=4)
    #         ax.xaxis.set_major_locator(plt.MaxNLocator(3))
    #         # ax.set_xticklabels([label.replace(" ", "\n") for label in x_vals])
    #         #create strings for title
    #         percent_change = ((y_vals[len(y_vals) - 1] - y_vals[0]) / y_vals[0]) * 100
    #         percent_change = round(percent_change, 2)
    #         changed, days = "", ""
    #         if num_days == "1":
    #             days = "the past 24 hours"
    #         elif num_days == "MAX" or num_days == "max":
    #             days = "Within Lifetime"
    #         else:
    #             days = "Past " + num_days + " Days"
    #         # change title based on percent
    #         if percent_change > 0:
    #             changed = "+"
    #         else:
    #             changed = ""
    #         percent_change = "{:,}".format(percent_change) # had to do it here because this converts it to a string, need it as a int above
    #         coin_label = self.change_cap(coin_label)
    #         title1 = coin_label + " " + changed + percent_change + "% - " + days
    #         plt.title(title1)
    #         plt.ylabel('Price - USD')
    #         plt.grid(mfc = "gray")
    #         plt.savefig('chart.png', edgecolor = 'black')
    #         return True
    #     else:
    #         return False
