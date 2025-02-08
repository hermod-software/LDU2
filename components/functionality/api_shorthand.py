import discord

from components.shared_instances import bot

async def is_user_banned(user_id: int, guild_id: int) -> bool:
    """checks if a user is banned in a guild"""
    guild = bot.get_guild(guild_id)
    if guild is None:
        raise ValueError("guild not found")

    bans = await guild.bans()

    try:
        for entry in bans:
            if entry.user.id == user_id:
                return True
            return False
    except discord.Forbidden:
        raise ValueError("bot does not have permission to view bans")
    except discord.HTTPException:
        raise ValueError("discord API error")
    
    
    