import discord
from discord.ext import commands
import os
import sys

from components.shared_instances import bot, tree
from components.function.logging import log

def log_all_commands():
    commands = bot.tree.get_commands()
    log(f"loaded {len(commands)} commands{":" if len(commands) else ""} {', '.join([command.name for command in commands])}")  

async def sync_tree():
    log("syncing tree...")
    await tree.sync()
    log_all_commands()

async def load_all_cogs():
    log("loading cogs...")
    # load all cogs in the components/cogs directory
    for file in os.listdir("components/cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"components.cogs.{file[:-3]}")
            log(f"loaded cog {file}")
    log("done loading cogs")


@bot.event
async def on_ready():
    log (f"~1l~2o~3r~4i~5t~6s~1i ~2b~3o~4t~5 ~r(colourtest)")
    log(f"~2successfully logged in as ~1{bot.user}")
    guilds_text = "guilds" if len(bot.guilds) != 1 else "guild"
    log(f"~2connected to {len(bot.guilds)} {guilds_text}: ~1{', '.join([guild.name for guild in bot.guilds])}")
    await load_all_cogs()
    
    # goes last always
    await sync_tree()

@bot.event
async def on_guild_join(guild):
    log(f"joined guild {guild.name}")
    await sync_tree()

@bot.event
async def on_guild_remove(guild):
    log(f"removed from guild {guild.name}")

with open("token.txt", "r") as f:
    token = f.read().strip()

bot.run(token)