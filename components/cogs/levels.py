import discord
from discord.ext import commands
import asyncio
import random
import time

from components.function.logging import log
from components.function.savedata import set_guild_attribute, get_guild_attribute
from components.classes.confighandler import ConfigHandler, register_config
import components.function.levels.basic as lvbsc

POINTS_DATABASE = {}
recent_speakers = {}

async def save_points_regular(interval=15):
    log(f"~2autosave coroutine started, interval: {interval}s")
    while True:
        await asyncio.sleep(interval)
        for guild_id, data in POINTS_DATABASE.items():
            set_guild_attribute(guild_id, "points_data", data)
        #log(f"~2saved points data for {len(POINTS_DATABASE)} guilds")



class Levels(commands.Cog):

    def __init__(self, bot: commands.Bot):
        global POINTS_DATABASE
        self.bot = bot
        self.generate_handlers()
        register_config("levels_config")

        POINTS_DATABASE = {}
        self.load_points_data()
        self.autosave_task = None  # track the autosave task
        self.startup_task = self.bot.loop.create_task(self._background_startup())

    async def _background_startup(self):
        await self.bot.wait_until_ready()
        log("~4levels cog background startup")
        if not self.autosave_task or self.autosave_task.done():
            log("~2starting points data autosave task (background task)")
            self.autosave_task = self.bot.loop.create_task(save_points_regular(15))
        else:
            log("~3autosave task already running (background task)")

    def generate_handlers(self):
        self.confighandlers = {}
        guilds = self.bot.guilds
        for guild in guilds:
            confighandler = ConfigHandler("levels_config", guild)
            self.confighandlers[guild.id] = confighandler

    def load_points_data(self):
        guilds = self.bot.guilds
        for guild in guilds:
            data = get_guild_attribute(guild.id, "points_data")
            if data is None:
                data = {}
            POINTS_DATABASE[guild.id] = data
            log(f"~2loaded points data for {guild.name}")


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        log(f"~2joined guild {guild.name}, regenerating handlers...")
        self.generate_handlers()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        log(f"~2removed from guild {guild.name}, regenerating handlers...")
        self.generate_handlers()

    def increment_user_points(self, user_id: int, guild_id: int, points: int):
        if guild_id not in POINTS_DATABASE:
            POINTS_DATABASE[guild_id] = {}
        if user_id not in POINTS_DATABASE[guild_id]:
            POINTS_DATABASE[guild_id][user_id] = 0
        POINTS_DATABASE[guild_id][user_id] += points

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        confighandler = self.confighandlers.get(message.guild.id, None)
        if confighandler is None:
            log(f"~1could not find config handler for guild {message.guild.name}")
            return

        timestamp = time.time()
        cooldown = confighandler.get_attribute("message_cooldown", fallback=30)

        last_spoke = recent_speakers.get(message.author.id)
        if last_spoke is not None and timestamp - last_spoke < cooldown:
            return
        recent_speakers[message.author.id] = timestamp
        guild_name = message.guild.name
        points_range = confighandler.get_attribute("points_range", fallback=(1, 5))

        user_level_pre = lvbsc.points_to_level(POINTS_DATABASE[message.guild.id].get(message.author.id, 0), guild=message.guild, confighandler=confighandler)

        points = random.randint(points_range[0], points_range[1])
        self.increment_user_points(message.author.id, message.guild.id, points)

        user_level_post = lvbsc.points_to_level(POINTS_DATABASE[message.guild.id].get(message.author.id, 0), guild=message.guild, confighandler=confighandler)

        if user_level_pre[0] != user_level_post[0]:
            await self.level_up(user_level_post[0], message.author, message.guild, confighandler)

        log(f"~2added {points} points to {message.author.name} in {guild_name}")
        new_points = POINTS_DATABASE[message.guild.id][message.author.id]
        await message.reply(f"you now have {new_points} points in {guild_name}. your level is {user_level_post[0]} and you need {user_level_post[1]} points to level up.")


    async def level_up(self, level, user: discord.User, guild: discord.Guild, confighandler: ConfigHandler, role_up=False):

        guild_name = guild.name

        alert_channel = confighandler.get_attribute("alert_channel")

        dm = False
        if alert_channel is None:
            dm = True
            alert_message = confighandler.get_attribute("levelup_message_dm") if not role_up else confighandler.get_attribute("roleup_message_dm")
        else:
            alert_message = confighandler.get_attribute("levelup_message") if not role_up else confighandler.get_attribute("roleup_message")

        if role_up:
            roles = confighandler.get_attribute("levels")
            role = roles.get(level, None)
            if role is None:
                log(f"~1level_up was called with role_up=True but no role found for level {level} in guild {guild_name}")
                return
            try:
                role = guild.get_role(role)
            except discord.NotFound:
                log(f"~1level_up was called with role_up=True but role {role} not found in guild {guild_name}")
                return
            try:
                await user.add_roles(role)
                log(f"~2added role {role.name} to {user.name} in {guild_name}")
            except discord.Forbidden:
                log(f"~1could not add role {role.name} to {user.name} in {guild_name}, bot does not have permission")
                return

        alert_message = alert_message.replace("{user}", user.mention)
        alert_message = alert_message.replace("{level}", str(level))
        alert_message = alert_message.replace("{guild}", guild_name)

        if dm:
            try:
                await user.send(alert_message)
                log(f"~2sent level up message to {user.name} in DM")
            except discord.Forbidden:
                log(f"~1could not send level up message to {user.name} in DM, user has DMs disabled")
                return
        else:
            channel = guild.get_channel(alert_channel)
            channel.send(alert_message)
            log(f"~2sent level up message to {user.name} in {channel.name}")


    @discord.app_commands.command(name="set_level_role", description="set a role to be given on level up")
    async def set_level_role(self, interaction: discord.Interaction, level: int, role: discord.Role):
        confighandler = self.confighandlers.get(interaction.guild.id, None)
        if confighandler is None:
            log(f"~1set_level_role: could not find config handler for guild {interaction.guild.name}")
            return
        
        if level <= 1:
            await interaction.response.send_message("level must be greater than 1", ephemeral=True)
            return
        
        if role not in interaction.guild.roles:
            await interaction.response.send_message("role not found in guild", ephemeral=True)
            return
        
        roles = confighandler.get_attribute("levels", fallback={})
        if level in roles:
            await interaction.response.send_message(f"level {level} already has a role assigned", ephemeral=True)
            return
        
        roles[level] = role.id
        confighandler.set_attribute("levels", roles)
        await interaction.response.send_message(f"set role {role.name} for level {level}", ephemeral=True)
        log(f"~2set level role {role.name} for level {level} in guild {interaction.guild.name}")

    @discord.app_commands.command(name="rank", description="get your rank in the leaderboard.")
    async def rank(self, interaction: discord.Interaction):
        pass

    @discord.app_commands.command(name="leaderboard", description="get the leaderboard for the guild.")
    async def leaderboard(self, interaction: discord.Interaction):
        confighandler = 0

            


async def setup(bot: commands.Bot):
    await bot.add_cog(Levels(bot))