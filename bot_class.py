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
import copy

class discord_bot:
    # api instance
    cg = CoinGeckoAPI()
    es = etherscan.Client(
        api_key=bot_ids.etherscan_api_key,
        cache_expire_after=5,
    )

    logging.basicConfig(filename="log.log", level=logging.INFO)

    global the_coin_list
    the_coin_list = copy.deepcopy(cg.get_coins_list())

    # functions to gather btc, eth, and any coins price
    def btc_status(self):
        price_data = self.cg.get_price(ids= 'bitcoin', vs_currencies='usd')
        price = price_data['bitcoin']['usd']
        if price != None:
            price = round(price,2)
            price = "{:,}".format(price)
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
            price = "{:,}".format(price)
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
                    mc = "$" + market_cap
                else:
                    mc = market_cap
                # market_cap = "{:,}".format(market_cap)
                coin_name = self.change_cap(coin_name)
                # embedResponse = discord.Embed(title=coin_name + " Info", color=0xFF8C00)
                embedResponse = discord.Embed(color=0xFF8C00)
                embedResponse.add_field(name= coin_name + " Price", value= "["  + "$" + str(price) + "](https://www.coingecko.com/en/coins/" + coin_label + ")", inline=False)
                embedResponse.add_field(name= coin_name + " Percent Change (24hr)", value= str(percent_change), inline=False)
                embedResponse.add_field(name= coin_name + " Market Cap", value= mc, inline=False)
                response1 = "```" + coin_name + "'s price: $" + str(price) + "\n" + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
                # response2 = "```" + coin_name + "'s price: $" + str(price) + ", " + "Percent Change (24h): " + str(percent_change) + "%" + "\n" + "Market Cap: $" + str(market_cap) + "```"
                return embedResponse
        return ""

    # retreive data and create candle chart of any coin
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
            plt.clf()
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

    # convert one coin in the amount of another
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
                embedResponse = discord.Embed(color=0x7A2F8F)
                embedResponse.add_field(name= first + " to " + second + " Conversion", value= str(num) + " " + first + " = " + str(conversion) + " " + second, inline=False)
                return embedResponse
        else:
            embedResponse = discord.Embed(color=0xF93A2F)
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

        embedResponse = discord.Embed(color = 0x00C09A)
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
        embedResponse = discord.Embed(color=0x0099E1)
        embedResponse.add_field(name = "Top Trending Coins on CoinGecko", value = output)
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


    help =  "```CryptoBot gives you sends live updates of " + \
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
    "   Golden Ratio Multiple Indicator (BTC): '!grm-chart" + "\n" + "\n" + \
    "   Puell Multiple Indicator (BTC): '!puell-chart" + "\n" + "\n" + \
    "   MVRV Z-Score Indicator (BTC): '!mvrv-chart" + "\n" + "\n" + \
    "   PI Cycle Top Indicator (BTC): '!pi-chart" + "\n" + "\n" + \
    "   ATH, ATL, Range Commands: '!ath [coin], !atl [coin], !range [coin]" + "\n" + "\n" + \
    "   Image Command: '!image [coin]" + "\n" + "\n" + \
    "   Defisocks: '!defisocks" + "\n" + "\n" + \
    "   ATH, ATL, Range: '!ath [coin], !atl [coin], !range [coin]" + "\n" + "\n" + \
    "Credits to CoinGecko® for the free API!```"
