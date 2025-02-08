import discord
from discord.ext import commands

from components.shared_instances import bot, tree
from components.functionality.savedata import set_guild_member_attribute
from components.functionality.api_shorthand import is_user_banned

bot = None

class Appeals(commands.Cog):
    def __init__(self, botinstance):
        global bot
        bot = botinstance

    @discord.app_commands.command(name="appeal", description="Appeal moderator action")
    async def appeal(self, interaction: discord.Interaction):
    # this command should be non-guild only. obviously, you can't do commands in a guild you're not in
    # so we need to somehow determine where the user is banned or muted
        if interaction.guild is not None:
            await interaction.response.send_message("This command is not available in guilds. Please use DMs.", ephemeral=True)
            return
        
        user_is_banned_in = []

        for guild in bot.guilds:
            if await is_user_banned(interaction.user.id, guild.id):
                user_is_banned_in.append(guild)

        if not user_is_banned_in:
            await interaction.response.send_message("You are not banned in any guilds!", ephemeral=True)
            return