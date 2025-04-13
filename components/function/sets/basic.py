import random

from components.function.sets.classes import SetGroup, SetItem
import components.function.sets.basic as itemsets
from components.function.logging import log
from components.shared_instances import set_database
from components.function.image import pil_to_discord, invert_image_hue

def get_random_card():

    if not set_database:
        log("tried to roll a card but no sets are loaded")
        return None
    
    set_group = random.choice(set_database)
    item = random.choice(set_group.items)

    return item

def roll_item_chance():
    chance = random.randint(1, 100)

    if chance == 1:
        return "misprint"
    elif chance <= 5:
        return "globular"
    elif chance <= 20:
        return "slimey"
    elif chance <= 50:
        return "shiny"
    else:
        return "regular"
    
async def do_message_check(message):

    chance = random.randint(1, 10)
    if not chance == 1:
        #log("rolled a " + str(chance))
        return

    card = itemsets.get_random_card()

    rarity = itemsets.roll_item_chance()

    card_image = card.image.copy()

    if rarity == "misprint":
        card_image = invert_image_hue(card_image)

    stamp = f"A {card.item_type.lower()} appeared: **{card.name.title()}**!\nset: {card.parent.name.title()}\nauthor: {card.parent.author}\nrarity: **{rarity.title()}**"

    log(f"{message.author} rolled a {card.name} from {card.parent.name} ({rarity})")

    attachment, buffer = pil_to_discord(card.name, card_image)

    try:
        dm = await message.author.create_dm()
        await dm.send(stamp, file=attachment)
    except Exception as e:
        log(f"failed to send DM to {message.author}: {e}")

    buffer.close()