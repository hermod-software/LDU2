import discord
import math
import operator
import random

from components.classes.confighandler import ConfigHandler
from components.function.savedata import get_guild_attribute
from components.shared_instances import bot, POINTS_DATABASE
from components.function.logging import log

def points_to_level(points: int, confighandler: ConfigHandler) -> tuple[int, int]:
    "returns level, remaining points to next level"

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
        level, points_to_next = points_to_level(points, confighandler)
        progress = get_user_progress(level, total_points, points_to_next, confighandler)

        entry = (displayname, username, user_id, level, total_points, points_to_next, progress)

        formatted_leaderboard.append(entry)

    return formatted_leaderboard

def is_valid_range(given_range):
    if not isinstance(given_range, tuple):
        return False
    if not len(given_range) == 2:
        return False
    both_are_int = ( isinstance(given_range[0], int) and isinstance(given_range[1], int) )
    return both_are_int
        

def increment_user_points(guild:discord.Guild, user:discord.User, amount, confighandler:ConfigHandler) -> tuple[int, bool]:
    """increment a users points with either a set integer amount or a integer range (amount can be int or a valid 2 integer tuple). 
    returns the new point value and a bool: True if the user has levelled up and False otherwise."""

    # type checking

    if isinstance(amount, tuple):
        if is_valid_range(amount):
            amount = random.randint(*amount)
        else:
            raise TypeError(f"tuple value {amount} passed to increment_user_points is not a valid range")
    elif not isinstance(amount, int):
        raise TypeError(f"value {amount} passed to increment_user_points is not an integer or valid tuple range")
    
    # validate existence of user & guild

    guild_id = guild.id
    guild_name = guild.name
    user_id = user.id
    user_name = user.name

    if guild_id not in POINTS_DATABASE:
        POINTS_DATABASE[guild_id] = {}
    if user_id not in POINTS_DATABASE[guild_id]:
        POINTS_DATABASE[guild_id][user_id] = 0

    # get their current level

    user_points_before = POINTS_DATABASE[guild_id][user_id]
    user_level_before, _  = points_to_level(user_points_before, confighandler)

    # increment the user's point value

    POINTS_DATABASE[guild_id][user_id] += amount

    # get their new level

    user_points_after = POINTS_DATABASE[guild_id][user_id]
    user_level_after, _ = points_to_level(user_points_after, confighandler)

    # check if they have levelled up

    has_levelled_up = user_level_before != user_level_after

    log(f"~2added {amount} points to {user_name} in {guild_name}")

    return user_points_after, has_levelled_up