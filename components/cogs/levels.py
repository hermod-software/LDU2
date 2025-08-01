import discord
from discord.ext import commands
import asyncio
import random
import time

from components.function.logging import log
from components.function.savedata import set_guild_attribute, get_guild_attribute
from components.classes.confighandler import ConfigHandler, register_config
from components.shared_instances import POINTS_DATABASE
import components.function.levels.basic as lvbsc
import components.function.levels.image_generation as lvimg

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

        # validation

        if message.author.bot or message.guild is None:
            return
        
        confighandler = self.confighandlers.get(message.guild.id, None)
        if confighandler is None:
            log(f"~1could not find config handler for guild {message.guild.name}")
            return

        # check if the user has sent a message within the cooldown

        timestamp = time.time()
        cooldown = confighandler.get_attribute("message_cooldown", fallback=30)

        last_spoke = recent_speakers.get(message.author.id)
        if last_spoke is not None and timestamp - last_spoke < cooldown:
            return
        recent_speakers[message.author.id] = timestamp

        # get the points range from the guild's config

        points_range = confighandler.get_attribute("points_range", fallback=(1, 5))

        # increment the points and check if a new role needs to be given

        new_points, has_levelled_up = lvbsc.increment_user_points(guild=message.guild, user=message.author, amount=points_range, confighandler=confighandler)
        new_level = lvbsc.points_to_level(new_points, confighandler)

        if has_levelled_up:
            await self.level_up(new_level, message.author, message.guild, confighandler)


    async def level_up(self, level, user: discord.User, guild: discord.Guild, confighandler: ConfigHandler):

        guild_name = guild.name


        # check if the user should be getting a new role here

        potential_rewards = confighandler.get_attribute("levels", fallback=None)
        if potential_rewards is not None:
            if level in potential_rewards:
                role_up = True
            else:
                role_up = False
        else:
            role_up = False

        # get strings for each situation

        config_keys = confighandler.get_attribute("keys")

        levelup_message_dm = config_keys["levelup_message_dm"]
        levelup_message = config_keys["levelup_message"]
        roleup_message_dm = config_keys["roleup_message_dm"]
        roleup_message = config_keys["roleup_message"]

        # decide which string to use

        alert_channel = confighandler.get_attribute("alert_channel")

        dm = ( alert_channel is None ) # passed through a variable so we can check later
        if dm:
            alert_message = roleup_message_dm if role_up else levelup_message_dm
        else:
            alert_message = roleup_message if role_up else levelup_message

        # try our best to give the role if applicable

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

        # format the strings and try our best to send them to the user

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
            await channel.send(alert_message)
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

    @discord.app_commands.command(name="unset_level_role", description="clear a level of rewards")
    async def unset_level_role(self, interaction: discord.Interaction, level: int):
        confighandler = self.confighandlers.get(interaction.guild.id, None)
        if confighandler is None:
            log(f"~1set_level_role: could not find config handler for guild {interaction.guild.name}")
            return
        
        if level <= 1:
            await interaction.response.send_message("level must be greater than 1", ephemeral=True)
            return
        
        roles = confighandler.get_attribute("levels", fallback={})
        if level in roles:
            del roles[level]
            await interaction.response.send_message(f"level {level} has been cleared of reward", ephemeral=True)
            log(f"~2cleared level role for level {level} in guild {interaction.guild.name}")
            confighandler.set_attribute("levels", roles)
            return
        else:
            await interaction.response.send_message(f"that level doesn't have a role reward, so it couldn't be deleted.", ephemeral=True)
            log(f"~2tried to clear level role for level {level} in guild {interaction.guild.name}, but there was no role to clear.")
        
    @discord.app_commands.command(name="get_role_list", description="get the list of role rewards for this server")
    async def get_role_list(self, interaction: discord.Interaction):
        allowed_mentions = discord.AllowedMentions.none()
        confighandler = self.confighandlers.get(interaction.guild.id, None)
        if confighandler is None:
            log(f"~1get_role_list: could not find config handler for guild {interaction.guild.name}")
            await interaction.response.send_message("there was an error with this guild's confighandler", ephemeral=True, allowed_mentions=allowed_mentions)
            return

        roles = confighandler.get_attribute("levels", fallback={})
        if not roles:
            await interaction.response.send_message("no level role rewards are set for this server.", ephemeral=True, allowed_mentions=allowed_mentions)
            return

        lines = []
        for lvl, role_id in sorted(roles.items()):
            role = interaction.guild.get_role(role_id)
            if role:
                lines.append(f"Level {lvl}: {role.mention}")
            else:
                lines.append(f"Level {lvl}: (role not found, id: {role_id})")

        msg = "level role rewards for this server:\n" + "\n".join(lines)
        await interaction.response.send_message(msg, allowed_mentions=allowed_mentions)
        



    @discord.app_commands.command(name="rank", description="get your rank in the leaderboard.")
    async def rank(self, interaction: discord.Interaction):
        confighandler = self.confighandlers.get(interaction.guild.id, None)
        if confighandler is None:
            log(f"~1rank: could not find config handler for guild {interaction.guild.name}")
            await interaction.response.send_message("there was an error with this guild's confighandler", ephemeral=True)
            return

        leaderboard = lvbsc.format_leaderboard(
            guild_id=interaction.guild.id,
            confighandler=confighandler
        )

        user_id = interaction.user.id
        user_entry = None
        for entry in leaderboard:
            if entry[2] == user_id:
                user_entry = entry
                break

        if not user_entry:
            await interaction.response.send_message("you are not on the leaderboard yet!", ephemeral=True)
            return

        colours = ["red", "blue", "green", "pink", "orange", "black", "grey"]
        theme = random.choice(colours)

        image_path = lvimg.generate_rank_card_image(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            leaderboard=leaderboard,
            user_requested=user_id,
            theme=theme
        )

        if not image_path:
            await interaction.response.send_message("sorry, there was an error trying to generate your rank card.", ephemeral=True)
            return

        image_path = str(image_path)
        file = discord.File(image_path, filename="rank_card.png")
        await interaction.response.send_message(file=file)


    # TODO: make themes a proper config thing

    @discord.app_commands.command(name="leaderboard", description="get the leaderboard for the guild.")
    async def leaderboard(self, interaction: discord.Interaction, page:int=1):
        confighandler = self.confighandlers.get(interaction.guild.id, None)
        if confighandler is None:
            log(f"~1leaderboard: could not find config handler for guild {interaction.guild.name}")
            return
        colours = ["red", "blue", "green", "pink", "orange", "black", "grey"]
        theme = random.choice(colours)

        leaderboard = lvbsc.format_leaderboard(
            guild_id=interaction.guild.id,
            confighandler=confighandler
        )

        image_path = lvimg.generate_leaderboard_image(
            guild_id=interaction.guild.id,
            guild_name=interaction.guild.name,
            leaderboard=leaderboard,
            max_rows=6,
            page_requested=page,
            theme=theme
        )

        image_path = str(image_path)

        file = discord.File(image_path, filename="leaderboard.png")

        await interaction.response.send_message(file=file)

            


async def setup(bot: commands.Bot):
    await bot.add_cog(Levels(bot))