import discord
from discord import app_commands
from discord.ext import commands
from bot_class import discord_bot

class all_commands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = discord_bot()
        super().__init__()  # this is now required in this context.

    # get the coin info
    @app_commands.command(name="c")
    async def get_coin(self, interaction: discord.Interaction, specific_coin: str, hidden: bool = False) -> None:
        """ Returns the 24hr change, price, and marketcap of a specific coin. """
        response = self.db.get_coin_price(specific_coin)
        await interaction.response.send_message(embed = response, ephemeral=hidden)

    # get the chart of one coin (against USD)
    @app_commands.command(name="chart")
    async def get_chart(self, interaction: discord.Interaction, specific_coin: str, num_days: int) -> None:
        """ Displays a coin's chart in a specific time frame. Type -1 for max days """
        if num_days == -1:
            num_days = "max"
        response = self.db.get_line_chart(specific_coin, "", str(num_days), 1)
        await interaction.response.send_message(file = discord.File('chart.png'), embed = response, ephemeral=False)

    # get the trendiest coins
    @app_commands.command(name="trendy")
    async def get_trendy(self, interaction: discord.Interaction) -> None:
        """ This yields the top 10 trendiest coins in the past 24hrs """
        response = self.db.get_trending()
        await interaction.response.send_message(embed = response, ephemeral=False)

    # get the supply of a token
    @app_commands.command(name="supply")
    async def get_supply(self, interaction: discord.Interaction, coin: str) -> None:
        """ Gets the circulating, total, and max supply for a token """
        response = self.db.get_supply(coin)
        await interaction.response.send_message(embed = response, ephemeral=False)
    
    # get the chart of one coin against another
    @app_commands.command(name="chart2")
    async def get_chart2(self, interaction: discord.Interaction, coin: str, coin_2: str, num_days: int) -> None:
        """ Displays a chart of one coin over another coin_2 in a specific time frame. Type -1 for max days """
        if num_days == -1:
            num_days = "max"
        response = self.db.get_line_chart(coin, coin_2, str(num_days), 2)
        await interaction.response.send_message(file = discord.File('chart.png'), embed = response, ephemeral=False)
    
    # get the tvl of a token
    @app_commands.command(name="tvl")
    async def get_tvl(self, interaction: discord.Interaction, coin: str) -> None:
        """ Gets the total value locked of a protocol"""
        response = self.db.get_tvl(coin)
        await interaction.response.send_message(embed = response, ephemeral=False)
    
    # get the marketcap to the total-value-locked ratio of a token
    @app_commands.command(name="tvl-ratio")
    async def get_tvl_ratio(self, interaction: discord.Interaction, coin: str) -> None:
        """ Gets the total value locked of a protocol"""
        response = self.db.get_mcap_to_tvl_ratio(coin)
        await interaction.response.send_message(embed = response, ephemeral=False)

    # get the ath of a token
    @app_commands.command(name="ath")
    async def get_ath(self, interaction: discord.Interaction, coin: str) -> None:
        """ Gets the all time high price (USD) of a token"""
        response = self.db.get_all_time("H", coin)
        await interaction.response.send_message(embed = response, ephemeral=False)

    # get the atl of a token
    @app_commands.command(name="atl")
    async def get_atl(self, interaction: discord.Interaction, coin: str) -> None:
        """ Gets the all time low price (USD) of a token"""
        response = self.db.get_all_time("L", coin)
        await interaction.response.send_message(embed = response, ephemeral=False)
    
    # get the range of a token
    @app_commands.command(name="range")
    async def get_range(self, interaction: discord.Interaction, coin: str) -> None:
        """ Gets the range (atl, range, ath in USD) of a token"""
        response = self.db.get_all_time("R", coin)
        await interaction.response.send_message(embed = response, ephemeral=False)

    
    # get a list of coins
    # @app_commands.command(name="list")
    # async def get_list(self, interaction: discord.Interaction, coin1: str, coin2: str, coin3: str, coin4: str = None, coin5: str = None) -> None:
    #     """ Shows you three coins of your choice  """
    #       fix by creating one long message
    #     coin_list = [coin1, coin2, coin3, coin4, coin5]
    #     for coin in coin_list:
    #         result = self.db.get_coin_price(coin)
    #         if result != "":
    #             await interaction.response.send_message(embed = result, ephemeral = True)
    #     await message.add_reaction('\N{THUMBS UP SIGN}')

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(all_commands(bot))
