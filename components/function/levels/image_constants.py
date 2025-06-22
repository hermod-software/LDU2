from PIL import Image, ImageDraw, ImageFont
from math import ceil
import time
import os
import timeit
from pathlib import Path

from function.logging import log

TEMP_IMAGE_PATH = Path("./savedata/temp/")
ASSETS_PATH = Path("./assets/")
TYPES_PATH = ASSETS_PATH / "type/"

# COLOURS

PALETTES = {
    "red": {
        "main": (172, 40, 71),
        "grey": (211, 50, 91),
        "text": (255,255,255),
        "circle": (29,27,29)
    },
    "blue": {
        "main": (92,91,142),
        "grey": (127,125,193),
        "text": (255,255,255),
        "circle": (29,27,29),
    },
    "green": {
        "main": (100, 169, 100),
        "grey": (123, 206, 123),
        "text": (255,255,255),
        "circle": (29,27,29),
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
    BIGNUMBER = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 135)
    MEDNUMBER = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 112)
    TITLE = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 90)
    BODY = ImageFont.truetype(f"{TYPES_PATH}typeface.otf", 45)
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

class Bounds: # a class to more easily handle bounding boxes and things we need from them
    def __init__(self, bounds):
        self.left = bounds[0]
        self.top = bounds[1]
        self.right = bounds[2]
        self.bottom = bounds[3]
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        self.hmiddle = round(self.left + self.width / 2) # can't be a float
        self.vmiddle = round(self.top + self.height / 2) # can't be a float
        self.centre = (self.hmiddle, self.vmiddle)

        self.topleft = (self.left, self.top)
        self.topright = (self.right, self.top)
        self.bottomleft = (self.left, self.bottom)
        self.bottomright = (self.right, self.bottom)

# LEVEL CIRCLE CONSTANTS

REAL_CIRCLE_DIMS = 55, 55
# width, height of actual post-scaling circle

C_HEIGHT, C_WIDTH = REAL_CIRCLE_DIMS[0] * 3, REAL_CIRCLE_DIMS[1] * 3
C_OFFSET = 1

A_OFFSET = 12
A_THICKNESS = 12
A_START = 0
A_END = 360

T_V_OFFSET = 8

A_START = A_START - 90  # rotate by -90 because PIL arc func starts at 3 o'clock for some reason

PADDING = C_OFFSET * 2
S_HEIGHT, S_WIDTH = C_HEIGHT + PADDING, C_WIDTH + PADDING # padding to prevent clipping
S_DIMS = (S_WIDTH, S_HEIGHT)
C_DIMS = (C_WIDTH, C_HEIGHT)