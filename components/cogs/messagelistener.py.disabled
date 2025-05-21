import discord
from discord.ext import commands

from components.function.logging import log
from components.function.image import pil_to_discord
import components.function.sets.basic as itemsets

class MessageListener(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.author.bot:
            return
        if message.guild is None:
            guildname = "DM"
        else:
            guildname = message.guild.name
        
        log(f"~1{message.author} ~rsent a message in ~1{guildname}~2{"#" if message.guild else ''}{message.channel.name if message.guild else ''}")
        
        await itemsets.do_message_check(message)

        


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageListener(bot))