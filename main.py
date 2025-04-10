import discord
from discord.ext import commands
import os
import sys

from components.shared_instances import bot, tree

def print_all_commands():
    print("commands loaded:")
    for command in bot.commands:
        print(command)
        

async def sync_tree():
    print("syncing tree...")
    await tree.sync()
    print("tree synced")
    print_all_commands()

async def load_all_cogs():
    for file in os.listdir("components/cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"components.cogs.{file[:-3]}")
            print(f"loaded cog {file}")
    print("done loading cogs")


@bot.event
async def on_ready():
    print(f"successfully logged in as {bot.user}")
    print(f"connected to {len(bot.guilds)} guilds: {', '.join([guild.name for guild in bot.guilds])}")
    await load_all_cogs()
    
    # goes last always
    await sync_tree()

@bot.event
async def on_guild_join(guild):
    print(f"joined guild {guild.name}")
    await sync_tree()

@bot.event
async def on_guild_remove(guild):
    print(f"removed from guild {guild.name}")

with open("token.txt", "r") as f:
    token = f.read().strip()

bot.run(token)