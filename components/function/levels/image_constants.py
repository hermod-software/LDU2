from PIL import Image, ImageDraw, ImageFont
from math import ceil
import time
import os
import timeit
from pathlib import Path

from components.function.logging import log

TEMP_IMAGE_PATH = Path("./savedata/temp/")
ASSETS_PATH = Path("./assets/")
TYPES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../assets/type/')

# COLOURS

PALETTES = {
    "red": {
        "main": (220, 50, 70),
        "dark": (170, 30, 50),
        "grey": (255, 100, 120),
        "text": (255, 255, 255),
        "circle": (40, 20, 30)
    },
    "blue": {
        "main": (70, 110, 220),
        "dark": (40, 70, 150),
        "grey": (120, 170, 255),
        "text": (255, 255, 255),
        "circle": (20, 30, 50),
    },
    "green": {
        "main": (60, 180, 90),
        "dark": (35, 120, 60),
        "grey": (120, 230, 160),
        "text": (255, 255, 255),
        "circle": (20, 40, 30),
    },
    "pink": {
        "main": (255, 119, 158),
        "dark": (175, 82, 109), 
        "grey": (135, 86, 100), 
        "text": (255, 255, 255),
        "circle": (15, 15, 15), 
    },
    "orange": {
        "main": (255, 140, 40),
        "dark": (200, 90, 10),
        "grey": (255, 200, 120),
        "text": (255, 255, 255),
        "circle": (60, 30, 10),
    },
    "black": {
        "main": (40, 40, 40),
        "dark": (25, 25, 25),
        "grey": (80, 80, 80),
        "circle": (15, 15, 15),
    },
    "grey": {
        "main": (150, 150, 150),
        "dark": (120, 120, 120),
        "grey": (200, 200, 200),
        "text": (230, 230, 230),
        "circle": (60, 60, 60),
    }
}

# top3 is in index order for the sake of easy retrieval
TOP3 = {
    0: (218, 177, 99),  # gold
    1: (176, 167, 184), # silver
    2: (181, 103, 43)   # bronze
}

# LOADING FONTS

try:  # be mindful of the file type if you are changing the font (ttf, otf, etc). this script is designed for monospace fonts!
    log("~2all fonts loaded successfully")
    BIGNUMBER = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 100)
    MEDNUMBER = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 90)
    TITLE = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 105)
    BODY = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 75)
    BODY_LIGHT = ImageFont.truetype(f"{TYPES_PATH}light.otf", 45)
    TINY = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 33)
    TINY_LIGHT = ImageFont.truetype(f"{TYPES_PATH}light.otf", 33)
except IOError:
    log("~1!! graphics.py could not find typeface.otf or light.otf, using default font for all !!")
    BIGNUMBER = ImageFont.load_default()
    MEDNUMBER = ImageFont.load_default()
    TITLE = ImageFont.load_default()
    BODY = ImageFont.load_default()
    BODY_LIGHT = ImageFont.load_default()
    TINY = ImageFont.load_default()
    TINY_LIGHT = ImageFont.load_default()
    # pil's load_default does not respect sizes so i guess it will just look weird
    # but it's better than crashing

# LEVEL CIRCLE CONSTANTS

C_HEIGHT, C_WIDTH = 165,165
C_OFFSET = 1            # padding around edge of circle to prevent clipping

# circle exp indicator arc constants

A_OFFSET = 12           # gap between edge of circle and edge of arc
A_THICKNESS = 12    
A_START = 0             # range of degrees to use for the exp indicator
A_END = 360             # 270 for example would use only 3 quarters for the indicator
A_START = A_START - 90  # rotate by -90 because PIL arc func starts at 3 o'clock for some reason

T_V_OFFSET = -8          # text vertical offset (positive = up)

# MAIN LEADERBOARD LAYOUT CONSTANTS

PADDING = C_OFFSET * 2
S_HEIGHT, S_WIDTH = C_HEIGHT + PADDING, C_WIDTH + PADDING # padding to prevent clipping
S_DIMS = (S_WIDTH, S_HEIGHT)
C_DIMS = (C_WIDTH, C_HEIGHT)

LB_WIDTH = 1800             # height is calculated dynamically based on amount of rows specified
LB_TITLEBAR_HEIGHT = 150    # height of titlebar at the top of image, only exists once
LB_TITLE_PADDING_U = 30
LB_TITLE_PADDING_L = 30
LB_TITLE_META_WIDTH = 345   # region reserved for date & page count
LB_TITLE_TEXT_WIDTH = LB_WIDTH - LB_TITLE_META_WIDTH

COLUMN_WIDTH = LB_WIDTH // 2    # column is half each of width
COLUMN_PADDING = (8, 8)         # edge, middle
LB_USER_UNIT_HEIGHT = 180
LB_USER_UNIT_WIDTH = COLUMN_WIDTH - (COLUMN_PADDING[0] + (COLUMN_PADDING[1] // 2))
# i.e. | 8 | user unit | 4 | 4 | user | 8 |
# uses full 8 of padding but for both shared in the middle
X_LEFT_COLUMN = COLUMN_PADDING[0]
X_RIGHT_COLUMN = COLUMN_WIDTH + COLUMN_PADDING[1] // 1

LB_C_PADDING = (LB_USER_UNIT_HEIGHT - C_HEIGHT) // 2


LB_USERNAME_V_PADDING = 0
LB_BOTTOM_V_PADDING = 30
LB_USER_TEXT_PAD = 15
X_LB_USER_TEXT = (LB_C_PADDING * 2) + C_WIDTH + LB_USER_TEXT_PAD
LB_USER_UNIT_TEXT_WIDTH = LB_USER_UNIT_WIDTH - ((LB_C_PADDING * 3) + C_WIDTH)

# i.e. | cpad | circle | cpad | text | cpad |
