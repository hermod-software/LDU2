import discord
from discord.ext import commands
import asyncio

from components.function.logging import log
from components.function.savedata import set_guild_attribute, get_guild_attribute
from components.classes.confighandler import ConfigHandler, register_config

POINTS_DATABASE = {}

async def save_points_regular(interval=30):
    while True:
        await asyncio.sleep(interval)
        for guild_id, data in POINTS_DATABASE.items():
            set_guild_attribute(guild_id, "points_data", data)

class Levels(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def generate_handlers(self):
        self.confighandlers = []
        guilds = self.bot.guilds
        for guild in guilds:
            confighandler = ConfigHandler("levels_config", guild)
            self.confighandlers.append(confighandler)

    def load_points_data(self):
        guilds = self.bot.guilds
        for guild in guilds:
            data = get_guild_attribute(guild.id, "points_data")
            if data is None:
                data = {}
            POINTS_DATABASE[guild.id] = data
            log(f"~2loaded points data for {guild.name}")


    @commands.Cog.listener()
    async def on_ready(self):
        log("~2loaded levels config")
        self.generate_handlers()

        POINTS_DATABASE = {}
        self.load_points_data()

        await asyncio.gather(
            save_points_regular(30),
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        log(f"~2joined guild {guild.name}, regenerating handlers...")
        self.generate_handlers()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        log(f"~2removed from guild {guild.name}, regenerating handlers...")
        self.generate_handlers()

    
        

            


async def setup(bot: commands.Bot):
    await bot.add_cog(Levels(bot))