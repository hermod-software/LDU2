# this file should not import any other files in the bot to avoid circular imports
# it is for storing "global" objects that are used across the whole bot

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True


bot = commands.Bot(intents=intents, command_prefix='drigoydgjamdiuhfnsgihfjsfthsft')

tree = bot.tree

logged_amount = 0