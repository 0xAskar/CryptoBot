import math
import bot_ids
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
import matplotlib.ticker as tick
import matplotlib.dates as mdates
import mplfinance as mpf
from pycoingecko import CoinGeckoAPI
import etherscan
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from PIL import Image
from pandas import Timestamp
import copy
# import seaborn as sbs
import time

class discord_bot:
    # api instance
    cg = CoinGeckoAPI()
    es = etherscan.Client(
        api_key=bot_ids.etherscan_api_key,
        cache_expire_after=5,
    )

    # logging.basicConfig(filename="log.log", level=logging.INFO)

    global the_coin_list
    the_coin_list = copy.deepcopy(cg.get_coins_list())

    # functions to gather btc, eth, and any coins price
    def get_crypto_price(self, crypto_id):
        try:
            url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={crypto_id}&x_cg_demo_api_key=CG-oGkFUu3WJx9geBKMN3Uekwbt"
            response = requests.get(url)
            data = response.json()
            
            if data and len(data) > 0:
                price = data[0]['current_price']
                if price is not None:
                    price = round(price, 2)
                    price = "{:,}".format(price)
                    return price
            return None
        except Exception as e:
            print(f"Error fetching {crypto_id} price: {str(e)}")
            return None

    def btc_status(self):
        price = self.get_crypto_price('bitcoin')
        if price is not None:
            return f"Bitcoin - ${price}"
        return "CoinGecko Error"

    def eth_status(self):
        price = self.get_crypto_price('ethereum')
        if price is not None:
            return f"Ethereum: ${price}"
        return "CoinGecko Error"

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
                price = "{:,}".format(price)
                percent_change = price_data[coin_label]['usd_24h_change']
                if percent_change != None:
                    percent_change = str(round(percent_change, 2)) + "%"
                else:
                    percent_change = None
                market_cap = price_data[coin_label]['usd_market_cap']
                market_cap = round(market_cap, 2)
                market_cap = self.check_large(market_cap)
                if market_cap != "Not Found":
                    mc = "$" + str(market_cap)
                else:
                    mc = str(market_cap)
                # market_cap = "{:,}".format(market_cap)
                coin_name = self.change_cap(coin_name)
                # embedResponse = discord.Embed(title=coin_name + " Info", color=0xFF8C00)
                embedResponse = discord.Embed(title = coin_name + "'s" + " Stats", color = 0xFF8C00, timestamp = datetime.utcnow())
                embedResponse.add_field(name= "Price", value= "["  + "$" + str(price) + "](https://www.coingecko.com/en/coins/" + coin_label + ")", inline=False)
                embedResponse.add_field(name= "Percent Change (24hr)", value= str(percent_change), inline=False)
                embedResponse.add_field(name= "Market Cap", value= mc, inline=False)
                embedResponse.set_footer(text = "Powered by cryptobot.info")
                response1 = "```" + coin_name + "'s price: $" + str(price) + "\n" + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
                # response2 = "```" + coin_name + "'s price: $" + str(price) + ", " + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
                return embedResponse
        return ""

    # retreive data and create candle chart of any coin

    def get_new_line_chart(self, coin_name, coin_name2, num_days, type):
        #all code that includes type 2 is for chart one currency against another

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

    def get_line_chart(self, coin_name, coin_name2, num_days, type):
        #all code that includes type 2 is for chart one currency against another

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
            plt.close()
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
            if type == 2:
                count = 0
                for point in charts2['prices']:
                    if count == min:
                        break
                    y_vals[count] = y_vals[count] / point[1]
                    count += 1
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
                days = " Within Lifetime"
            else:
                days = "Over Past " + num_days + " Days"
            # change title based on percent
            color = "#37FFA1" # green
            if percent_change > 0:
                changed = "+"
            else:
                color = '#FF5252' # red
                changed = ""

            percent_change = "{:,}".format(percent_change) # had to do it here because this converts it to a string, need it as a int above
            # title = "\n" + "\n" + coin_label + "'s price " + changed + percent_change + "% within " + days
            coin_label = self.change_cap(coin_label)
            title1 = "\n" + "\n" + coin_label + " Price Change: " + changed + percent_change + "%"
            title2 = coin_label + " Price Change " + days
            if type == 2:
                coin_label2 = self.change_cap(coin_name2.lower())
                title1 = "\n" + "\n" + coin_label + "/" + coin_label2 + " Price Change: " + changed + percent_change + "%"
                title2 = "\n" + "\n" + coin_label + "/" + coin_label2 + " Price Change " + days
            mc = mpf.make_marketcolors(
                                up='tab:blue',down='tab:red',
                                wick={'up':'blue','down':'red'},
                                volume='tab:green',
                               )
            # edited_style  = mpf.make_mpf_style(gridstyle = '-', facecolor = "lightgray", gridcolor = "white", edgecolor = "black", base_mpl_style = "classic", marketcolors=mc)
            edited_style  = mpf.make_mpf_style(gridcolor = "white", facecolor = "181818", edgecolor = "white", base_mpf_style = "mike", marketcolors=mc)
            wconfig = {
                "line_width" : 2
            }
            if type == 1:
                fig, axlist = mpf.plot(ohlc, type='line', title = title1, figratio = (30,20), ylabel = 'Price - USD', style = edited_style, update_width_config=wconfig, linecolor = color, returnfig = True)
                ax1 = axlist[0]
                # ax1.yaxis.set_major_formatter(tick.FormatStrFormatter('%.8f'))
                ax1.yaxis.set_major_formatter(tick.FuncFormatter(reformat_large_tick_values))
                fig.savefig('chart.png', bbox_inches = "tight")
            else:
                fig, axlist = mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = coin_label + "/" + coin_label2, style = edited_style, update_width_config=wconfig, linecolor = color, returnfig = True)
                ax1 = axlist[0]
                # ax1.yaxis.set_major_formatter(tick.FormatStrFormatter('%.8f'))
                ax1.yaxis.set_major_formatter(tick.FuncFormatter(reformat_large_tick_values))
                fig.savefig('chart.png', bbox_inches = "tight")
            embed = discord.Embed(title = title2, color= 0x92c8f5, timestamp = datetime.utcnow()) #creates embed
            embed.set_image(url="attachment://chart.png")
            embed.set_footer(text = "Powered by cryptobot.info")
            return embed
        else:
            return "error"

    def get_tvl_chart(self, coin_name, coin_name2, num_days, type):
        #coin label work
        coin_label = ""
        coin_name = coin_name.lower()
        coin_label = self.check_coin(coin_name)
        #coin label 2 work

        valid_intervals = ["1w", "1m", "3m", "1y", "all", "max"]
        check_int = False
        num_days = num_days.lower()
        for interval in valid_intervals:
            if num_days == interval:
                check_int = True
        if not check_int:
            error_days = "```Command Error: Wrong number of days: Only can input '1w','1m','3m','1y','all','max'```"
            return error_days

        if type == 2:
            coin_label2 = ""
            coin_name2 = coin_name2.lower()
            coin_label2 = self.check_coin(coin_name2)

        if self.check_coin(coin_name) != "":
            link = "https://data-api.defipulse.com/api/v1/defipulse/api/GetHistory?api-key=" + bot_ids.defipulse_api_key + "&project="+coin_name+"&period=" + num_days
            response = requests.get(link)
            output = response.json()
            y_vals = []
            x_vals = []
            count = 0
            min = len(output)
            volume = []
            for one_int in output:
                time_conv = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(one_int["timestamp"]))

                x_vals.append(time_conv)
                y_vals.append(one_int["tvlUSD"])
                volume.append(1)
                count += 1
            # check to see if the data is reversed
            if x_vals[0] > x_vals[1]:
                # reverse lists
                x_vals = x_vals[::-1]
                y_vals = y_vals[::-1]
            plt.close()
            open, close, high, low = y_vals, y_vals, y_vals, y_vals
            period = len(open)
            frequency = ""
            # if num_days == "1":
            #     frequency = "5min"
            # elif num_days != "max" and (int(num_days) <= 90 and int(num_days) > 1):
            #     frequency = "1H"
            # else:
            #     frequency = "4D"
            dti = pd.date_range(start = x_vals[0], end = x_vals[len(x_vals)-1], periods = period)
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
            # if num_days == "1":
            #     days = "the past 24 hours"
            # elif num_days == "MAX" or num_days == "max":
            #     days = "Within Lifetime"
            # else:
            #     days = "Past " + num_days + " Days"
            # # change title based on percent
            # if percent_change > 0:
            #     changed = "+"
            # else:
            #     changed = ""

            percent_change = "{:,}".format(percent_change) # had to do it here because this converts it to a string, need it as a int above
            # title = "\n" + "\n" + coin_label + "'s price " + changed + percent_change + "% within " + days
            coin_label = self.change_cap(coin_label)
            title1 = "\n" + "\n" + coin_label + " " + "Historcal TVL: " + percent_change + "% - " + "Past " + num_days
            if type == 2:
                coin_label2 = self.change_cap(coin_name2.lower())
                title1 = "\n" + "\n" + coin_label + "/" + coin_label2 + " " + changed + percent_change + "% - " + days
            mc = mpf.make_marketcolors(
                                up='tab:blue',down='tab:red',
                                wick={'up':'blue','down':'red'},
                                volume='tab:green',
                               )
            edited_style  = mpf.make_mpf_style(gridstyle = '-', gridcolor = "white", edgecolor = "black", base_mpl_style = "mike", marketcolors=mc)
            # edited_style  = mpf.make_mpf_style(gridstyle = '-', facecolor = "black", gridcolor = "white", edgecolor = "black", base_mpl_style = "classic", marketcolors=mc)
            if type == 1:
                fig, axlist = mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = 'Price - USD ($)', style = "nightclouds", returnfig = True)
                ax1 = axlist[0]
                # ax1.yaxis.set_major_formatter(tick.FormatStrFormatter('%.8f'))
                ax1.yaxis.set_major_formatter(tick.FuncFormatter(reformat_large_tick_values))
                fig.savefig('ctvl.png', bbox_inches='tight')
            else:
                fig, axlist = mpf.plot(ohlc, type='line', title = title1, figratio = (16,10), ylabel = coin_label + "/" + coin_label2, style = edited_style, returnfig = True)
                fig.savefig('ctvl.png', bbox_inches='tight')
            embed = discord.Embed(title = title1, url = "cryptobot.info", color= 0xFF8C00, timestamp = datetime.utcnow()) #creates embed
            embed.set_image(url="attachment://ctvl.png")
            embed.set_footer(text = "Powered by cryptobot.info")
            return embed
        else:
            return "error"

    # retreive data and create candle chart of any coin
    def get_candle_chart(self, coin_name, num_days):

        # used the below links for the mpf libraries
        # https://github.com/matplotlib/mplfinance#usage
        # https://github.com/matplotlib/mplfinance/blob/master/examples/styles.ipynb

        #coin label work
        coin_label = ""
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
            plt.close()
            date_arr, year, month, day, hour, open, high, low, close, volume = [], [], [], [], [], [], [], [], [], []
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

    # function to get the ath, atl, and/or the range of the coin
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
                embedResponse = discord.Embed(color=0xFF8C00, timestamp = datetime.utcnow())
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
                    embedResponse = discord.Embed(title= coin_final + " Range", color=0x0000ff, timestamp = datetime.utcnow())
                    embedResponse.add_field(name= "All Time Low", value= "$" + str(atl), inline=True)
                    embedResponse.add_field(name= "Current Price", value= "$" + str(price), inline=True)
                    embedResponse.add_field(name= "All Time High", value= "$" + str(ath), inline=True)
                    embedResponse.set_footer(text = "Powered by cryptobot.info")
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
        if first_data != None:
            second_data = self.cg.get_price(ids= second_coin, vs_currencies='usd')
            second_price = second_data[second_coin]['usd']
            if second_data != None:
                # convert to proper cap.
                first = self.change_cap(first)
                second = self.change_cap(second)
                conv_num = float(num) * (first_price / second_price)
                conversion = self.round_num(conv_num)
                conversion = self.check_large(conversion)
                num = self.check_large(int(num))
                embedResponse = discord.Embed(color=0x7A2F8F, timestamp = datetime.utcnow())
                embedResponse.add_field(name= first + " to " + second + " Conversion", value= str(num) + " " + first + " = " + str(conversion) + " " + second, inline=False)
                embedResponse.set_footer(text = "Powered by cryptobot.info")
                return embedResponse
        else:
            embedResponse = discord.Embed(color=0x7A2F8F, timestamp = datetime.utcnow())
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
        csupply = data["market_data"]["circulating_supply"]
        tsupply = data["market_data"]["total_supply"]
        msupply = data["market_data"]["max_supply"]

        coin_name = self.change_cap(coin_name)
        csupply = self.check_large(csupply)
        tsupply = self.check_large(tsupply)
        msupply = self.check_large(msupply)

        embedResponse = discord.Embed(title = coin_name + "'s" + " Supply", color = 0x00C09A, timestamp = datetime.utcnow())
        embedResponse.add_field(name = "Circulating", value = csupply, inline=False)
        embedResponse.add_field(name = "Total", value = tsupply, inline=False)
        embedResponse.add_field(name = "Max", value = msupply, inline=False)
        embedResponse.set_footer(text = "Powered by cryptobot.info")
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
        embedResponse = discord.Embed(color=0x0099E1, timestamp = datetime.utcnow())
        embedResponse.add_field(name = "Top Trending Coins on CoinGecko", value = output)
        embedResponse.set_footer(text = "Powered by cryptobot.info")
        return embedResponse

    # find trending coins on coingecko
    def get_rekt(self):
        count = 0
        # link = "https://data-api.defipulse.com/api/v1/rekto/api/top10?api-key=" + bot_ids.defipulse_api_key
        # link = "https://api.rek.to/api/top10?api-key=" + bot_ids.defipulse_api_key
        # response = requests.get(link)
        # output = response.json()
        # ids, amounts = "", ""
        # for idiot in output["top10"]:
        #     if count < 5:
        #         ids += str(idiot["id"]) + "\n"
        #         amounts += "$" + str(self.check_large(idiot["value_usd"])) + "\n"
        #         # amounts += str(self.check_large(int(idiot["value_usd"]))) +  "\n"
        #         count += 1
        # embedResponse = discord.Embed(title="Top 5 Rekts (Past 24hrs)", color=0x6d37da)
        # embedResponse.add_field(name = "Rekted Amount (USD)", value = amounts)
        # embedResponse.add_field(name = "The Rekt-ed", value = ids)
        embedResponse = discord.Embed(title="Error with API", color=0x6d37da, timestamp = datetime.utcnow())
        embedResponse.add_field(name = "Depreciated", value = "Defipulse deprecated the Rekt API endpoints")
        return embedResponse


    def get_mcap_to_tvl_ratio(self, coin):
        coin_name = ""
        coin_name = self.check_coin(coin)
        # check if the coin names are valid
        if coin_name == "":
            return "e"
        data = self.cg.get_coin_by_id(id= coin_name)
        ratio = data["market_data"]["mcap_to_tvl_ratio"]
        coin_name = self.change_cap(coin_name)
        embedResponse = discord.Embed(color = 0xF8C300, timestamp = datetime.utcnow())
        embedResponse.add_field(name = coin_name + " Mcap to TVL Ratio", value = str(ratio), inline=False)
        embedResponse.set_footer(text = "Powered by cryptobot.info")
        return embedResponse

    def get_tvl(self, coin):
        coin_name = ""
        coin_name = self.check_coin(coin)
        # check if the coin names are valid
        if coin_name == "":
            return "e"
        data = self.cg.get_coin_by_id(id= coin_name)
        try:
            tvl = data["market_data"]["total_value_locked"]["usd"]
            tvl = self.check_large(tvl)
        except:
            tvl = "None"
        coin_name = self.change_cap(coin_name)
        embedResponse = discord.Embed(color = 0xF8C300, timestamp = datetime.utcnow())
        embedResponse.add_field(name = coin_name + " TVL", value = str(tvl), inline=False)
        embedResponse.set_footer(text = "Powered by cryptobot.info")
        return embedResponse

    def get_gmr(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path = "/root/cryptobot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/golden-ratio-multiplier/")
        driver.execute_script("window.scrollTo(0, 260)")
        sleep(5)
        screenshot = driver.save_screenshot("grm.png")
        img = Image.open("grm.png")
        width, height = img.size
        img = img.crop((50, 0, width-10, height-200))
        img = img.save("grm.png", format = "png")
        driver.quit()

    def get_mvrv(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path = "/root/cryptobot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/mvrv-zscore/")
        driver.execute_script("window.scrollTo(0, 290)")
        sleep(5)
        screenshot = driver.save_screenshot("mvrv.png")
        img = Image.open("mvrv.png")
        width, height = img.size
        img = img.crop((0, 0, width-10, height-205))
        img = img.save("mvrv.png", format = "png")
        driver.quit()

    # The Puell Multiple Chart
    def get_puell(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path = "/root/cryptobot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/puell-multiple/")
        driver.execute_script("window.scrollTo(0, 300)")
        sleep(5)
        screenshot = driver.save_screenshot("puell.png")
        img = Image.open("puell.png")
        width, height = img.size
        img = img.crop((10, 0, width-10, height-220))
        img = img.save("puell.png", format = "png")
        driver.quit()

    # The Pi Cycle Top Indicator
    def get_pi(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path = "/root/cryptobot/chromedriver", options = options)
        driver.get("https://www.lookintobitcoin.com/charts/pi-cycle-top-indicator/")
        driver.execute_script("window.scrollTo(0, 270)")
        sleep(5)
        screenshot = driver.save_screenshot("picycle.png")
        img = Image.open("picycle.png")
        width, height = img.size
        img = img.crop((10, 0, width-10, height-205))
        img = img.save("picycle.png", format = "png")
        driver.quit()

    def get_ds(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("window-size=1024,768")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path = "/root/cryptobot/chromedriver", options = options)
        driver.get("https://www.defisocks.com/#/")
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0,2):
            # Scroll down to bottom
            if i == 1:
                driver.execute_script("window.scrollTo(0, 3350);")
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
        img = img.crop((320, 125, width-340, height-100))
        img = img.save("ds.png", format = "png")
        driver.quit()

    def get_defisocks(self):
        results = self.es.get_token_transactions(contract_address = "0x9d942bd31169ed25a1ca78c776dab92de104e50e")
        return results
    # functions to check coins, names, and size

    # round numbers correctly, sig figs for <1, rounding for >1
    def round_num(self, num):
        if num < 1:
            temp = num
            count = 1
            while temp < 1:
                temp *= 10
                count += 1
            return round(num, count)
        else:
            return round(num, 2)

    def check_coin(self, coin_name):
        coin_label = ""
        coin_name = coin_name.lower()
        if coin_name == "uni":
            coin_name = "uniswap"
        elif coin_name == "rbc":
            coin_name = "rubic"
        elif coin_name == "comp" or coin_name == "compound":
            coin_name = "compound-governance-token"
        elif coin_name == "graph" or coin_name == "thegraph":
            coin_name = "the-graph"
        for coin in the_coin_list:
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
        for coin in the_coin_list:
            if coin['id'] == coin_name or coin['symbol'] == coin_name:
                if coin['symbol'] == coin_name:
                    coin_label = coin_name.upper()
                else:
                    coin_label = coin_name.lower()
                    coin_label = coin_label.capitalize()
                return coin_label
        return coin_label

    def check_large(self, num): #there are better ways but atm, its not important
        num = float(num)
        # check to see if num exists or less than 999, if so no need to compress
        if num == None:
            return "None"
        if num < 999:
            return num
        if num == 0:
            return "Not Found"
        #start compressing
        letter = ""
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
        embedResponse = discord.Embed(title="Gas Price", color=0x0000ff, timestamp = datetime.utcnow())
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

    def get_servers(self, bot):
        all = ""
        counter = 1
        for guild in bot.guilds:
            mem_count = guild.member_count
            all += "Server " + str(counter) + ": " + str(guild.name) + " (Size: " + str(mem_count) + ")" + "\n"
            counter += 1
        return all


    def help(self):
        help_info =  "```CryptoBot gives you sends live updates of " + \
        "any cryptocurrency!" + "\n" + "\n" + \
        "Commands:" + "\n" + "\n" + \
        "   Price Command: ![coin symbol/name], '!btc' or '!bitcoin' - retreive price information about a coin" + "\n" + "\n" + \
        "   Chart Command: '!chart btc 5' <chart> <coin> <num days> - retreive the line chart of a coin, only support USD as of now (ex: !chart link 30)" + "\n" + "\n" + \
        "   Chart Command: '!chart btc 5' <chart> <coin1> <coin2> <num days> - retreive the line chart of two coins coupled (ex: !chart link btc 30)" + "\n" + "\n" + \
        "   Candle Command: '!candle btc 5' <chart> <coin_name/symbol> <num days>, "\
        "days has to be one of these:" + "\n" + "   '1','7','14','30','90','180','365','MAX' - retreive the candle chart of a coin" + "\n" + "\n" + \
        "   Suggestion Command: !suggestion or !suggestions do this' <suggestion> <message> - send a suggestion for the bot" + "\n" + "\n" + \
        "   Gas Command: '!gas' - get information about gwei prices" + "\n" + "\n" + \
        "   Convert Command: '!convert <num> <coin1> <coin2>' - get conversion rate of num of coin1 in number of coin2 (ex: !convert 1000 usdc btc)" + "\n" + "\n" + \
        "   Global Defi Stats Command: '!global-defi' - get global information about defi" + "\n" + "\n" + \
        "   Top Trending Coins Command: '!trendy - get the top trending coins on CoinGecko" + "\n" + "\n" + \
        "   Supply Command: '!supply <coin> - get the circulating and maximum supply of a coin" + "\n" + "\n" + \
        "   Golden Ratio Multiple Indicator (BTC) (Unavailable): '!grm-chart" + "\n" + "\n" + \
        "   Puell Multiple Indicator (BTC) (Unavailable): '!puell-chart" + "\n" + "\n" + \
        "   MVRV Z-Score Indicator (BTC) (Unavailable): '!mvrv-chart" + "\n" + "\n" + \
        "   PI Cycle Top Indicator (BTC) (Unavailable): '!pi-chart" + "\n" + "\n" + \
        "   ATH, ATL, Range Commands: '!ath [coin], !atl [coin], !range [coin]" + "\n" + "\n" + \
        "   Image Command: '!image [coin]" + "\n" + "\n" + \
        "   TVL Command: '!tvl [coin]" + "\n" + "\n" + \
        "   Mcap to TVL Ratio Command: '!tvl-ratio [coin]" + "\n" + "\n" + \
        "   Defisocks (Unavailable): '!defisocks" + "\n" + "\n" + \
        "   ATH, ATL, Range: '!ath [coin], !atl [coin], !range [coin]" + "\n" + "\n" + \
        "Credits to CoinGecko® and Etherscan® for their free APIs!```"

        return help_info;




#############  end of discord_bot class ###############


def reformat_large_tick_values(tick_val, pos):
    """
    Turns large tick values (in the billions, millions and thousands) such as 4500 into 4.5K and also appropriately turns 4000 into 4K (no zero after the decimal).
    """
    check = True
    if (tick_val < 0.00000000000001 or tick_val == 0):
        return tick_val;
    if tick_val >= 1000000000:
        val = round(tick_val/1000000000, 1)
        new_tick_format = '{:}B'.format(val)
    elif tick_val >= 1000000:
        val = round(tick_val/1000000, 1)
        new_tick_format = '{:}M'.format(val)
    elif tick_val >= 1000:
        val = round(tick_val/1000, 1)
        new_tick_format = '{:}K'.format(val)
    elif tick_val > 100:
        new_tick_format = round(tick_val, 3)
    elif tick_val > 0.1:
        new_tick_format = round(tick_val, 1)
    else:
        new_tick_format = tick_val
        check = False
        check2 = True
        x = 1
        exp = 1
        while (check2):
            if tick_val > x:
                check2 = False

            x /= 10
            exp += 1
        new_tick_format = round(tick_val, exp)

    if check == True:
        # make new_tick_format into a string value
        new_tick_format = str(new_tick_format)

        # code below will keep 4.5M as is but change values such as 4.0M to 4M since that zero after the decimal isn't needed
        index_of_decimal = new_tick_format.find(".")

        if index_of_decimal != -1:
            value_after_decimal = new_tick_format[index_of_decimal+1]
            if value_after_decimal == "0":
                # remove the 0 after the decimal point since it's not needed
                new_tick_format = new_tick_format[0:index_of_decimal] + new_tick_format[index_of_decimal+2:]

    return new_tick_format
