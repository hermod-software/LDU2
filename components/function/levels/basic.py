import discord
import math

from components.classes.confighandler import ConfigHandler

def points_to_level(points: int, guild: discord.Guild, confighandler: ConfigHandler) -> tuple[int, int]:

    base = confighandler.get_attribute("base")
    growth_rate = confighandler.get_attribute("growth_rate")
    
    level = 0
    total_required = base
    cumulative_points = 0

    while points >= total_required:
        cumulative_points += total_required     # add points needed for the current level
        points -= total_required                # deduct points for the current level
        level += 1                              # increment level
        total_required = math.floor(base * (growth_rate ** level))  # points needed for the next level

    remaining_points = total_required - points

    return level, remaining_points