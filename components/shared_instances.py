# this file should not import any other files in the bot to avoid circular imports
# it is for storing "global" objects that are used across the whole bot

version = "proto"

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True


bot = commands.Bot(intents=intents, command_prefix='drigoydgjamdiuhfnsgihfjsfthsft')
# idiot prefix that i can't turn off so i made it very long such that nobody will ever trigger it

tree = bot.tree

# logger

logged_amount = 0