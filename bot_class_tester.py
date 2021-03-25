import math
import bot_ids
import logging
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
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from PIL import Image

class discord_bot:
    # api instance
    cg = CoinGeckoAPI()
    es = etherscan.Client(
        api_key= bot_ids.etherscan_api_key,
        cache_expire_after=5,
    )
    logging.basicConfig(filename='log_test.txt', level=logging.DEBUG)

    # functions to gather btc, eth, and any coins price
    def btc_status(self):
        price_data = self.cg.get_price(ids= 'bitcoin', vs_currencies='usd')
        price = price_data['bitcoin']['usd']
        if price != None:
            price = round(price,2)
            response = "Bitcoin - $" + str(price)
            logging.info("Logged BTC price at " + str(datetime.now()))
            return response
        else:
            logging.warning("Error from CoinGecko at: " + str(datetime.now()))
            return "CoinGecko Error"

    def eth_status(self):
        price_data = self.cg.get_price(ids= 'Ethereum', vs_currencies='usd')
        price = price_data['ethereum']['usd']
        if price != None:
            price = round(price,2)
            response = "Ethereum: $" + str(price)
            logging.info("Logged ETH price at " + str(datetime.now()))
            return response
        else:
            logging.warning("Error from CoinGecko at: " + str(datetime.now()))
            return "Coingecko Errors"

    def get_coin_price(self, coin_name):
        coin_label = ""
        coin_name = coin_name.lower()
        coin_label = self.check_coin(coin_name)
        if self.check_coin(coin_name) != "":
            price_data = self.cg.get_price(ids= coin_label, vs_currencies='usd', include_24hr_change='true', include_market_cap = 'true')
            price = price_data[coin_label]['usd']
            if price != None:
                if float(price) < 0.001:
                    price = round(price, 5)
                elif float(price) < 0.01:
                    price = round(price, 4)
                else:
                    price = round(price,3)
                # format price for commas
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
    def get_line_chart(self, coin_name, coin_name2, num_days, type):
        #coin label work
        coin_label = ""
        coin_name = coin_name.lower()
        coin_label = self.check_coin(coin_name)
        #coin label 2 work
        if type == 2:
            coin_label2 = ""
            coin_name2 = coin_name2.lower()
            coin_label2 = self.check_coin(coin_name2)

        #checking if num days is valid
        temp = str(num_days)
        if not temp.isdigit():
            temp = temp.lower()
            if temp != "max":
                return False

        if self.check_coin(coin_name) != "":
            charts = self.cg.get_coin_market_chart_by_id(id = coin_label, vs_currency='usd', days = num_days)
            if type == 2:
                charts2 = self.cg.get_coin_market_chart_by_id(id = coin_label2, vs_currency = 'usd', days = num_days)
            plt.clf()
            x_vals = []
            y_vals = []
            count = 0
            open, close, high, low, volume = [], [], [], [], []
            min = len(charts["prices"])
            if type == 2:
                if min > len(charts2["prices"]):
                    min = len(charts2["prices"])
            for point in charts['prices']:
                if count == 0:
                    time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
                    time1 = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                if count == 1:
                    time2 = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                if count == min-1:
                    time_end = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
                x_vals.append(time_conv)
                y_vals.append(point[1])
                volume.append(1)
                count += 1
                if count == min:
                    break
            # print(y_vals)
            # print("")
            # print("")
            if type == 2:
                count = 0
                for point in charts2['prices']:
                    if count == min:
                        break
                    y_vals[count] = y_vals[count] / point[1]
                    count += 1
            # print(y_vals)
            # times = [time1, time2]
            # year1, year2, month1, month2, day1, day2, hour1, hour2, min1, min2, sec1, sec2 = [0,'Y'],[0,'Y'],[0,'M'],[0,'M'],[0,'D'],[0,'D'],[0,'H'],[0,'H'],[0,'M'],[0,'M'],[0,'S'],[0,'S']
            # date_stamp = [year1, month1, day1, hour1, min1, sec1, year2, month2, day2, hour2, min2, sec2]
            # time_increments = [[0,4], [5,7], [8,10], [11,13], [14,16], [17,20]]
            # for time in times:
            #     count = 0
            #     for t in range(0:len(time))
            #         for increment in date_stamp:
            #             time[t:t+1]
            #             count += 1
            # count = 0
            # for time in times:
            #     for increment in time_increments:
            #         date_stamp[count][0] = int(time[increment[0]:increment[1]])
            #         count += 1
            # change = 0
            # new_period = ""
            # this would keep the
            # for i in range(0, len(time_increments)):
            #     temp = date_stamp[i+len(time_increments)][0] - date_stamp[i][0]
            #     if temp > 0:
            #         change = temp
            #         new_frequency = str(change) + date_stamp[i][1]
            #         break
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
            dti = pd.date_range(start = time_conv, end = time_end, periods = period)
            # print(dti2)
            # dti = pd.date_range(time_conv, periods=period, freq=frequency)
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
            if type == 2:
                coin_label2 = self.change_cap(coin_name2.lower())
                title1 = "\n" + "\n" + coin_label + "/" + coin_label2 + " " + changed + percent_change + "% - " + days
            mc = mpf.make_marketcolors(
                                up='tab:blue',down='tab:red',
                                wick={'up':'blue','down':'red'},
                                volume='tab:green',
                               )

            edited_style  = mpf.make_mpf_style(gridstyle = '-', facecolor = "lightgray", gridcolor = "white", edgecolor = "black", base_mpl_style = "classic", marketcolors=mc)
            if type == 1:
                mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = 'Price - USD', style = edited_style, savefig = "chart.png")
            else:
                mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = coin_label + "/" + coin_label2, style = edited_style, savefig = "chart.png")
            return ""
        else:
            return "error"

    # # chart of two coins for instance link/btc
    # def get_line_chart_two(self, coin_name, coin_name2, num_days):
    #     #coin label work
    #     coin_label = ""
    #     coin_label2 = ""
    #     coin_name = coin_name.lower()
    #     coin_label2 = coin_name2.lower()
    #     coin_label = self.check_coin(coin_name)
    #     coin_label2 = self.check_coin(coin_name2)
    #     #checking if num days is valid
    #     temp = str(num_days)
    #     if not temp.isdigit():
    #         temp = temp.lower()
    #         if temp != "max":
    #             return False
    #
    #     if self.check_coin(coin_name) != "":
    #         charts = self.cg.get_coin_market_chart_by_id(id = coin_label, vs_currency='usd', days = num_days)
    #         charts2 = self.cg.get_coin_market_chart_by_id(id = coin_label2, vs_currency = 'usd', days = num_days)
    #         plt.clf()
    #         x_vals = []
    #         y_vals = []
    #         count = 0
    #         open, close, high, low, volume = [], [], [], [], []
    #         min = len(charts["prices"])
    #         if min > len(charts2["prices"]):
    #             min = len(charts2["prices"])
    #         for point in charts['prices']:
    #             if count == min:
    #                 break
    #             if count == 0:
    #                 time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
    #             x_vals.append(time_conv)
    #             y_vals.append(point[1])
    #             volume.append(1)
    #             count += 1
    #         count = 0
    #         for point in charts2['prices']:
    #             if count == min:
    #                 break
    #             y_vals[count] = y_vals[count] / point[1]
    #             count += 1
    #         # create the date and dataframe
    #         open = y_vals
    #         close = y_vals
    #         high = y_vals
    #         low = y_vals
    #         period = len(open)
    #         frequency = ""
    #         if num_days == "1":
    #             frequency = "5min"
    #         elif num_days != "max" and (int(num_days) <= 90 and int(num_days) > 1):
    #             frequency = "1H"
    #         else:
    #             frequency = "4D"
    #         dti = pd.date_range(time_conv, periods=period, freq=frequency)
    #         ohlc = {"opens":open, "highs":high, "lows":low, "closes":close, "volumes":volume}
    #         ohlc = pd.DataFrame(data = ohlc, index = dti)
    #         ohlc.columns = ['Open', 'High', 'Low', 'Close', 'Volume'] #these two lines solved the dataframe problem
    #         ohlc.index.name = "Date"
    #         # plot and make it look good
    #         percent_change = ((close[len(close) - 1] - close[0]) / close[0]) * 100
    #         percent_change = round(percent_change, 2)
    #         changed, days = "", ""
    #         # change title based on days
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
    #
    #         percent_change = "{:,}".format(percent_change) # had to do it here because this converts it to a string, need it as a int above
    #         # title = "\n" + "\n" + coin_label + "'s price " + changed + percent_change + "% within " + days
    #         coin_label = self.change_cap(coin_name.lower())
    #         coin_label2 = self.change_cap(coin_name2.lower())
    #         title1 = "\n" + "\n" + coin_label + "/" + coin_label2 + " " + changed + percent_change + "% - " + days
    #         mc = mpf.make_marketcolors(
    #                             up='tab:blue',down='tab:red',
    #                             wick={'up':'blue','down':'red'},
    #                             volume='tab:green',
    #                            )
    #
    #         edited_style  = mpf.make_mpf_style(gridstyle = '-', facecolor = "lightgray", gridcolor = "white", edgecolor = "black", base_mpl_style = "classic", marketcolors=mc)
    #         mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = coin_label + "/" + coin_label2, style = edited_style, savefig = "chart.png")
    #         return ""
    #     else:
    #         return "error"


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
                if count == 0:
                    time1 = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                if count == 1:
                    time2 = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                if count == len(candles)-1:
                    time_end = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
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
            dti = pd.date_range(start = time_conv, end = time_end, periods = period)
            # dti = pd.date_range(time_conv, periods=period, freq=frequency)
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

    # add volume charts TODO
    def get_volume_chart(self, num_days):
        # list of exchanges
        exchange_ids = ["binance", "gdax", "uniswap"]
        exchange_names = ["Binance", "Coinbase Pro", "Uniswap"]
        volumes = []
        # get exchange data and input into volume list
        for ex in exchange_ids:
            volumes.append(self.cg.get_exchanges_volume_chart_by_id(id = ex, days = num_days))
        plt.clf()
        x_vals = []
        y_vals = []
        count = 0
        binance, gdax, uniswap = [], [], []
        output_volumes = [binance, gdax, uniswap]
        # find minimum for number of datapoints
        min = len(volumes[0])
        for vol in volumes:
            if len(vol) < min:
                min = len(vol)
        # now enter the datapoints into column
        for vol, output in zip(volumes, output_volumes):
            for point in vol:
                if count == 0:
                    time_conv = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
                    time1 = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                if count == 1:
                    time2 = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                if count == min-1:
                    time_end = datetime.utcfromtimestamp(point[0] / 1000).strftime('%Y-%m-%d')
                x_vals.append(time_conv)
                output.append(point[1])
                count += 1
                if count == min:
                    break
        print(output_volumes)
        return

    def get_all_time(self, symbol, coin_name):
        coin = ""
        coin = self.check_coin(coin_name)
        if coin == "":
            return "e"
        # get market data
        market_data = self.cg.get_coin_by_id(id = coin)
        ath = market_data["market_data"]["ath"]["usd"]
        atl = market_data["market_data"]["atl"]["usd"]
        # change the coin name capitalization
        coin_final = self.change_cap(coin)
        # then deduce based on type of prompt
        if symbol == "H":
            if ath != None and ath != "":
                ath = "{:,}".format(ath)
                embedResponse = discord.Embed(color=0xFF8C00)
                embedResponse.add_field(name= coin_final + " ATH", value= "$" + str(ath), inline=False)
                return embedResponse
            else:
                return "e"

        elif symbol == "L":
            if atl != None and atl != "":
                atl = "{:,}".format(atl)
                embedResponse = discord.Embed(color=0xFF8C00)
                embedResponse.add_field(name= coin_final + " ATL", value= "$" + str(atl), inline=False)
                return embedResponse
            else:
                return "e"
        elif symbol == "R":
            if ath != None and atl != None and ath != "" and atl != "":
                # get ath and atl prices
                ath = "{:,}".format(ath)
                atl = "{:,}".format(atl)
                # get current price
                price_data = self.cg.get_price(ids= coin, vs_currencies='usd', include_24hr_change='true', include_market_cap = 'true')
                price = price_data[coin]['usd']
                if price != None:
                    if float(price) < 0.001:
                        price = round(price, 5)
                    elif float(price) < 0.01:
                        price = round(price, 4)
                    else:
                        price = round(price,3)
                    # format price for commas
                    price = "{:,}".format(price)
                    embedResponse = discord.Embed(title= coin_final + " Range", color=0x0000ff)
                    embedResponse.add_field(name= "All Time Low", value= "$" + str(atl), inline=True)
                    embedResponse.add_field(name= "Current Price", value= "$" + str(price), inline=True)
                    embedResponse.add_field(name= "All Time High", value= "$" + str(ath), inline=True)
                    return embedResponse
                else:
                    return "e"
            else:
                return "e"


    # get an image of a coin
    def get_image(self, coin_name):
        coin = ""
        coin = self.check_coin(coin_name)
        if coin == "":
            return "e"
        # get coin image data
        output = self.cg.get_coin_by_id(id = coin)
        image_url = image_cg = output["image"]["small"]
        # change the coin name capitalization
        coin_final = self.change_cap(coin)

        # take image and save as png
        req = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'})
        # webpage = urlopen(req).read()
        file = open("image.png", "wb")
        file.write(req.content)
        file.close()
        return coin_final

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
        if first_price != None:
            second_data = self.cg.get_price(ids= second_coin, vs_currencies='usd')
            second_price = second_data[second_coin]['usd']
            if second_price != None:
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
        else:
            embedResponse = discord.Embed(color=0x7A2F8F)
            embedResponse.add_field(name= "Error", value = "No data from CoinGecko", inline=False)
            return embedResponse
        return embedResponse

    def get_supply(self, coin):
        coin_name = ""
        coin_name = self.check_coin(coin)
        # check if the coin names are valid
        if coin_name == "":
            return "e"

        data = self.cg.get_coin_by_id(id= coin_name)
        print(data["market_data"])
        csupply = data["market_data"]["circulating_supply"]
        tsupply = data["market_data"]["total_supply"]
        msupply = data["market_data"]["max_supply"]

        coin_name = self.change_cap(coin_name)
        tsupply = self.check_large(tsupply)
        csupply = self.check_large(csupply)
        msupply = self.check_large(msupply)

        embedResponse = discord.Embed(color = 0x969C9F)
        embedResponse.add_field(name = coin_name + " Circulating Supply", value = csupply, inline=False)
        embedResponse.add_field(name = coin_name + " Total Supply", value = tsupply, inline=False)
        embedResponse.add_field(name = coin_name + " Max Supply", value = msupply, inline=False)
        return embedResponse

    # find trending coins on coingecko
    def get_trending(self):
        numbering = range(1,8)
        output = ""
        trendy = self.cg.get_search_trending()
        count = 0
        for x in trendy["coins"]:
            output += str(numbering[count]) + ") " + x['item']['name'] + "\n"
            count += 1
        embedResponse = discord.Embed(color=0xF8C300)
        embedResponse.add_field(name = "Top Trending Coins on CoinGecko", value = output)
        return embedResponse

    # Golden Ratio Multiple Chart
    def get_gmr(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(executable_path = "/Users/askar/Documents/Bots/CryptoBot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/golden-ratio-multiplier/")
        driver.execute_script("window.scrollTo(0, 260)")
        sleep(5)
        screenshot = driver.save_screenshot("grm.png")
        img = Image.open("grm.png")
        width, height = img.size
        img = img.crop((50, 0, width-10, height-10))
        img = img.save("grm.png", format = "png")
        driver.quit()

    # MVRV Z-Score Chart
    def get_mvrv(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(executable_path = "/Users/askar/Documents/Bots/CryptoBot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/mvrv-zscore/")
        driver.execute_script("window.scrollTo(0, 290)")
        sleep(5)
        screenshot = driver.save_screenshot("mvrv.png")
        img = Image.open("mvrv.png")
        width, height = img.size
        img = img.crop((0, 0, width-10, height-20))
        img = img.save("mvrv.png", format = "png")
        driver.quit()

    # The Puell Multiple Chart
    def get_puell(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(executable_path = "/Users/askar/Documents/Bots/CryptoBot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/puell-multiple/")
        driver.execute_script("window.scrollTo(0, 300)")
        sleep(5)
        screenshot = driver.save_screenshot("puell.png")
        img = Image.open("puell.png")
        width, height = img.size
        img = img.crop((10, 0, width-10, height-30))
        img = img.save("puell.png", format = "png")
        driver.quit()

    # The Pi Cycle Top Indicator
    def get_pi(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(executable_path = "/Users/askar/Documents/Bots/CryptoBot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/pi-cycle-top-indicator/")
        driver.execute_script("window.scrollTo(0, 270)")
        sleep(5)
        screenshot = driver.save_screenshot("picycle.png")
        img = Image.open("picycle.png")
        width, height = img.size
        img = img.crop((10, 0, width-10, height-30))
        img = img.save("picycle.png", format = "png")
        driver.quit()

    def get_ds(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(executable_path = "/Users/askar/Documents/Bots/CryptoBot/chromedriver", options = options)
        driver.get("https://defisocks.com/#/")
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0,2):
            # Scroll down to bottom
            if i == 1:
                driver.execute_script("window.scrollTo(0, 3800);")
            # Wait to load page
            sleep(4)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        screenshot = driver.save_screenshot("ds.png")
        img = Image.open("ds.png")
        width, height = img.size
        img = img.crop((280, 125, width-280, height-60))
        img = img.save("ds.png", format = "png")
        driver.quit()


    def get_defisocks(self):
        results = self.es.get_token_transactions(contract_address = "0x9d942bd31169ed25a1ca78c776dab92de104e50e")
        return results
    # functions to check coins, names, and size: helper functions

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
        if coin_name == "uni":
            coin_name = "uniswap"
        elif coin_name == "graph" or coin_name == "thegraph":
            coin_name = "the-graph"
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
        if num == None:
            return "None"
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
        embedResponse = discord.Embed(color=0xF93A2F)
        embedResponse.add_field(name= "Error", value= "Not a valid command/coin", inline=False)
        return embedResponse

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
