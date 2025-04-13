import discord
from discord.ext import commands

from components.function.logging import log

class LevelsConfig(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    

        


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelsConfig(bot))