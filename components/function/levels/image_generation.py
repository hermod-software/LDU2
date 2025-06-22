
from PIL import Image, ImageDraw, ImageFont
from math import ceil, pi, sin, cos, tan
import time
import os
import timeit

import components.function.levels.image_constants as C
import components.function.levels.basic as b

# dear PIL...
# i HATE YOU
# but you make this possible
# happy valentines 21th june 2025



def get_page(leaderboard, max_rows=5, page_requested=1) -> tuple[list, bool]:
    """bool is whether or not we don't have enough entries to full up a page"""

    # return a "page" from the leaderboard
    # page 1 - index 0-9
    # page 2 - index 10-19
    # page 3 - index 20-29
    # and so on.. depending on params.
    # where n is page requested and x is max rows, y is max entries (2x)
    # n = 3
    # y = 10
    # lower = y * (n - 1) = 20
    # upper = lower + y = 30 (BUT this is ok since slicing is upper exclusive)

    max_entries = max_rows * 2

    if len(leaderboard) < max_entries:
        # not enough entries to have more than 1 page
        return leaderboard, True 
    
    lower_bound = max_entries * (page_requested - 1)    # y * (n - 1)
    upper_bound = lower_bound + max_entries             # l + y

    # no need to check if there is actually enough pages.
    # we will check beforehand, and slicing does not raise
    # if we go OOB anyway.

    return leaderboard[lower_bound:upper_bound], False 
    
# base resolution is 600 x 360
# we will render at 1800 x 900 and then scale down because PIL will not do anti aliasing :(

# entry format: 0 DISPLAY NAME, 1 USER NAME, 2 UUID, 3 LEVEL, 4 TOTAL POINTS, 5 POINTS TO NEXT LEVEL, 6 PROGRESS

def generate_leaderboard_image(guild_id: int, leaderboard: list, max_rows: int, page_requested: int, theme: str = "red") -> str:
    "returns the path of the leaderboard image"

    def generate_progress_circle(entry, lb_index, theme):
        if lb_index in C.TOP3:
            text_colour = C.TOP3[lb_index]  
            # get the "reward colour" (gold, silver, bronze) for top 3 users
        else:
            text_colour = C.PALETTES[theme]["text"] 
            # get the text colour for requested theme

        chars = len(str(entry[3])) # level (4th element)
        if chars == 1:
            font = C.BIGNUMBER
        elif chars == 2:
            font = C.MEDNUMBER
        elif chars == 3:
            font = C.TITLE
        # the font size should respect the width of the circle
        # hope and pray to god that nobody ever gets a 4 digit level

        surface = Image.new("RGBA", C.S_DIMS) 
        # dimensions specied in image_constants
        draw = ImageDraw.Draw(surface)
        draw.ellipse(
            (
                C.C_OFFSET,
                C.C_OFFSET,
                C.C_OFFSET + C.C_WIDTH, 
                C.C_OFFSET + C.C_HEIGHT
            ),
            fill=C.PALETTES[theme]["circle"]
        )
        draw.arc(
            (
                C.A_OFFSET,
                C.A_OFFSET,
                C.S_WIDTH - C.A_OFFSET,
                C.S_HEIGHT - C.A_OFFSET
            ),
            start=C.A_START,
            end=C.A_START + C.A_END * entry[6],
            fill=text_colour,
            width=C.A_THICKNESS
        )
        midpoint = (C.CIRCWIDTH // 2, C.CIRCHEIGHT // 2)
        draw.text(
            xy=(
                midpoint[0],
                midpoint[1] - C.T_V_OFFSET 
                # inverted because up is down in PIL apparently
            ),
            text=f"{entry[3]}", # level (4th element)
            font=font,
            fill=text_colour,
            anchor="mm"
        )

        result = surface.resize(
            size=(C.REAL_CIRCLE_DIMS[0], C.REAL_CIRCLE_DIMS[1]),
            resample=Image.LANCZOS
        )

        mask = result.split()[3] 

        return result, mask

    def generate_user_unit(entry, lb_index):


    lb_page_data = get_page(leaderboard, max_rows, page_requested)

