import discord
import math

from components.classes.confighandler import ConfigHandler
from components.function.savedata import get_guild_attribute

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

def get_guild_leaderboard(guild_id: int) -> list[tuple[int, int]]:
    points_db = get_guild_attribute(guild_id, "points_data")
    if points_db is None:
        return [] # no data
    leaderboard = sorted(points_db.items(), key=lambda item: item[1], reverse=True)
    return leaderboard

def get_user_position(guild_id:int, target_user_id:int) -> int:
    leaderboard = get_guild_leaderboard(guild_id)

    for user_id, _ in leaderboard:
        if user_id == target_user_id:
            