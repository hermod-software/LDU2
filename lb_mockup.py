from PIL import Image, ImageDraw, ImageFont

LB_WIDTH, LB_TITLEBAR_HEIGHT = 1800, 150
LB_USER_UNIT_HEIGHT = 180
C_WIDTH = C_HEIGHT = 165
PADDING = 1 * 2
COLUMN_WIDTH = LB_WIDTH // 2
COLUMN_PADDING = (8, 8)
LB_USER_UNIT_WIDTH = COLUMN_WIDTH - (COLUMN_PADDING[0] + (COLUMN_PADDING[1] // 2))

rows_per_column = 5
img_height = LB_TITLEBAR_HEIGHT + rows_per_column * LB_USER_UNIT_HEIGHT
img = Image.new('RGB', (LB_WIDTH, img_height), color='white')
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

draw.rectangle([0, 0, LB_WIDTH, LB_TITLEBAR_HEIGHT], fill=(200, 200, 200))
draw.text((20, 50), "LEADERBOARD TITLE", fill='black', font=font)

def draw_user_block(x, y, username, level):
    cx = x + COLUMN_PADDING[0]
    cy = y + (LB_USER_UNIT_HEIGHT - C_HEIGHT) // 2 + PADDING
    draw.ellipse([cx, cy, cx + C_WIDTH, cy + C_HEIGHT], outline='black', width=2)
    text = f"Lvl {level}"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx + C_WIDTH/2 - tw/2, cy + C_HEIGHT/2 - th/2 - 8), text, fill='black', font=font)
    draw.text((cx + C_WIDTH + 20, cy + C_HEIGHT/2 - th/2), username, fill='black', font=font)

for col in range(2):
    for row in range(rows_per_column):
        x = col * COLUMN_WIDTH
        y = LB_TITLEBAR_HEIGHT + row * LB_USER_UNIT_HEIGHT
        uname = f"User{row + col*rows_per_column + 1}"
        lvl = (row + col*rows_per_column + 1) * 5
        draw_user_block(x, y, uname, lvl)

img.save("leaderboard_mockup.png")
