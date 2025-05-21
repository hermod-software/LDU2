from discord.ext import commands

from components.function.logging import log
from components.classes.confighandler import ConfigHandler

class ConfigHandlerCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log("~2loaded config handler commands")

async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigHandlerCommands(bot))