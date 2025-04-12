import discord
from discord.ext import commands

from components.function.logging import log

class MessageListener(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return  # Ignore messages from the bot itself
        
        log(message.content)

        


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageListener(bot))