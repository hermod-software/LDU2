import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents, command_prefix='qpoweiru')
# i'm using a random prefix here because i want to use only slash commands
# qpoweiru is an improbable thing to type by accident (letters on opposite sides of the keyboard)

tree = bot.tree