import discord
from discord.ext import commands
import os
import yaml
from pathlib import Path



ROOT_DIR = Path(__file__).parents[2]
DEFAULT_CONFIGS_DIR = ROOT_DIR / "components" / "assets" / "default_configs"

from components.function.logging import log
from components.function.savedata import set_guild_attribute, get_guild_attribute

COG_CONFIGS = {}

def register_config(label: str):
    COG_CONFIGS[label] = get_default_config(label)
    log(f"~2registered config {label}")

def get_default_config(config_name: str):
    if config_name not in COG_CONFIGS:
        raise ValueError(f"config {config_name} not registered")
    
    path = DEFAULT_CONFIGS_DIR / f"{config_name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"config file {config_name} is registered but has no file")
    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    return config

class ConfigHandler:
    """generic config handler for all configs"""

    def __init__(self, label: str, guild: discord.Guild):

        self.label = label
        self.guild = guild
        self.guild_id = guild.id
        self.guild_name = guild.name
        self.config = None


    def load_config(self):
        default_config = get_default_config(self.label)
        """loads the config for this guild."""
        config = get_guild_attribute(self.guild_id, self.label)
        if config is None:
            log(f"~1{self.guild_name} does not have attribute {self.label} config, initialising it with default settings...")
            config = default_config
        log(f"~2loaded levels config for {self.guild_name}")
        self.default_config = default_config

    def save_config(self):
        """saves the config for this guild."""
        set_guild_attribute(self.guild_id, key=self.label, value=self.config)
        log(f"~2saved levels config for {self.guild_name}")

    def get_attribute(self, attribute, fallback=None):
        if self.config is None:
            self.load_config()
        if attribute in self.config:
            try:
                return self.config[attribute]
            except Exception as e:
                log(f"~1error getting attribute {attribute} from config {self.label} for guild {self.guild_name}: {e}")
                return fallback
        else:
            log(f"~1attribute {attribute} not found in config {self.label} for guild {self.guild_name}, returning fallback")
            return fallback

