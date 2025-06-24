import discord
import math
import operator

from components.classes.confighandler import ConfigHandler
from components.function.savedata import get_guild_attribute
from components.shared_instances import bot
from components.function.logging import log

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

def level_to_points(level: int, confighandler: ConfigHandler) -> int:
    base = confighandler.get_attribute("base")
    growth_rate = confighandler.get_attribute("growth_rate")
    total_points = 0
    for l in range(level):
        total_points += math.floor(base * (growth_rate ** l))
    return total_points

def get_guild_leaderboard(guild_id: int) -> list[tuple[int, int]]:
    points_db = get_guild_attribute(guild_id, "points_data")
    if not isinstance(points_db, dict):
        log("~1tried to get guild leaderboard, failed due to missing or malformed data")
        return [] # no data or malformed data
    log("~2attempting to sort leaderboard data")
    leaderboard = sorted(points_db.items(), key=operator.itemgetter(1), reverse=True)
    log("~2successfully sorted leadboard data")
    return leaderboard

def get_user_position(guild_id: int, target_user_id: int) -> int:
    leaderboard = get_guild_leaderboard(guild_id)

    for position, (user_id, points) in enumerate(leaderboard):
        if user_id == target_user_id:
            return position + 1
    return -1 # if the user is not found in the leaderboard

def get_user_progress(level, total, points_to_next_level, confighandler):

    points_for_current_level = level_to_points(level, confighandler)
    points_since_last_level = total - points_for_current_level

    try:
        progress = points_since_last_level / (points_since_last_level + points_to_next_level)
        progress = min(progress, 1)
        progress = max(progress, 0)
    except ZeroDivisionError:
        progress = 1

    return progress

# DISPLAY NAME, USER NAME, UUID, LEVEL, TOTAL POINTS, POINTS TO NEXT LEVEL, PERCENT PROGRESS

def format_leaderboard(guild_id: int, confighandler: ConfigHandler) -> list[tuple[str, str, int, int, int, int]]:
    """returns a list of tuples: \n\nDISPLAY NAME, USER NAME, UUID, LEVEL, TOTAL POINTS, POINTS TO NEXT LEVEL"""
    leaderboard = get_guild_leaderboard(guild_id)

    formatted_leaderboard = []
    for user_id, points in leaderboard:
        user = bot.get_user(user_id)

        if not user:
            continue # skip if no such user exists

        displayname = user.display_name
        username = user.name
        total_points = int(points)
        level, points_to_next = points_to_level(points, bot.get_guild(guild_id), confighandler)
        progress = get_user_progress(level, total_points, points_to_next, confighandler)

        entry = (displayname, username, user_id, level, total_points, points_to_next, progress)

        formatted_leaderboard.append(entry)

    return formatted_leaderboard
