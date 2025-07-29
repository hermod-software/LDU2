import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, Button, View

from components.function.logging import log
from components.function.savedata import set_guild_attribute, get_guild_attribute
from components.classes.confighandler import ConfigHandler

class TestModal(Modal, title="test modal"):
    input = TextInput(
        label="test label",
        placeholder="test placeholder",
        style=discord.TextStyle.short,
        min_length=3,
        max_length=16,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"you entered: {self.input.value}", ephemeral=True)

class LevelsConfig(commands.Cog):


    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="test_modal", description="test modal")
    async def test_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TestModal())

            


async def setup(bot: commands.Bot):
    await bot.add_cog(LevelsConfig(bot))