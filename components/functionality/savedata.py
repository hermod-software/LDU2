import discord
import os
import yaml

from components.shared_instances import bot

# BASIC READ/WRITE FUNCTIONS ============================================================================================

def load_yaml(yaml_path: str) -> dict:
    """loads a yaml file as a dictionary. returns an empty dictionary if the file does not exist"""
    assert yaml_path.endswith(".yaml"), "yaml_path must end with .yaml"
    assert os.path.exists(os.path.dirname(yaml_path)), "directory does not exist"
    assert os.path.exists(yaml_path), "file does not exist"

    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def read_attribute(yaml_path: str, key: str):
    """reads a top-level attribute from the specified yaml file, returns None if the attribute is not set"""
    assert yaml_path.endswith(".yaml"), "yaml_path must end with .yaml"
    assert os.path.exists(os.path.dirname(yaml_path)), "directory does not exist"
    assert os.path.exists(yaml_path), "file does not exist"

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data.get(key, None)
    except (FileNotFoundError, yaml.YAMLError):
        return None

def set_attribute(yaml_path: str, key: str, value=True) -> None:
    """sets an attribute in the specified yaml file, default value is True"""
    assert yaml_path.endswith(".yaml"), "yaml_path must end with .yaml"
    assert os.path.exists(os.path.dirname(yaml_path)), "directory does not exist"
    # we obviously don't want to assert that the file exists because we may be creating it here

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        data = {}

    data[key] = value

    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

# USER DATA ============================================================================================================

user_data_dir = os.path.join(os.getcwd(), "savedata", "userdata")
os.makedirs(user_data_dir, exist_ok=True)

def set_guild_member_attribute(guild_id: int, member_id: int, key: str, value=True) -> None:
    """sets a user's attribute in the user data directory, default value is True"""

    user_data_path = os.path.join(user_data_dir, str(guild_id))
    os.makedirs(user_data_path, exist_ok=True)
    user_data_path = os.path.join(user_data_path, f"{member_id}.yaml")

    set_attribute(user_data_path, key, value)


def get_guild_member_attribute(guild_id: int, member_id: int, key: str):
    """gets a user's attribute from the user data directory. returns none if attribute is not set"""

    user_data_path = os.path.join(user_data_dir, str(guild_id), f"{member_id}.yaml")

    return read_attribute(user_data_path, key)

def get_attribute_for_all_members(guild_id: int, key: str) -> dict:
    """gets an attribute value for all users in a guild.\n\nreturns a dictionary of user ids and values.\n\nusers without the attribute are not included"""

    user_list = os.listdir(os.path.join(user_data_dir, str(guild_id)))

    user_data = {}

    for user in user_list:
        if not user.endswith(".yaml"):
            continue
        user = user.replace(".yaml", "")
        user_value = get_guild_member_attribute(guild_id, int(user), key)
        if user_value is not None:
            user_data[int(user)] = user_value

    return user_data
    
# GUILD DATA ===========================================================================================================

guild_data_dir = os.path.join(os.getcwd(), "savedata", "guilddata")
os.makedirs(guild_data_dir, exist_ok=True)

def set_guild_attribute(guild_id: int, key: str, value=True):
    """sets a guild's attribute in the guild data directory, default value is True"""

    guild_data_path = os.path.join(guild_data_dir, f"{guild_id}.yaml")

    set_attribute(guild_data_path, key, value)

def get_guild_attribute(guild_id: int, key: str):
    """gets a guild's attribute from the guild data directory. returns none if attribute is not set"""

    guild_data_path = os.path.join(guild_data_dir, f"{guild_id}.yaml")

    return read_attribute(guild_data_path, key)