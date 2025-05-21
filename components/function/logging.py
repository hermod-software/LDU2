import datetime

from components.shared_instances import logged_amount

COLOURS = {
    "1": "\033[31m",      # red
    "2": "\033[32m",      # green
    "3": "\033[33m",      # yellow
    "4": "\033[34m",      # blue
    "5": "\033[35m",      # magenta
    "6": "\033[36m",      # cyan
    "7": "\033[37m",      # white
}
# ~r is reset code

COLOUR_ROTATION = ["7", "6"] # console will cycle through these colours when printing text

def log(message):
    global logged_amount
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    reset_colour = COLOUR_ROTATION[logged_amount % len(COLOUR_ROTATION)]

    new_message = []

    colour_assign_mode = False
    for char in message:
        if colour_assign_mode:
            if char in COLOURS:
                new_message.append(COLOURS[char])
            elif char == "r":
                new_message.append(COLOURS[reset_colour])
            colour_assign_mode = False
            continue
        if char == "~":
            colour_assign_mode = True
            continue
        else:
            new_message.append(char)
    new_message = "".join(new_message)

    print(f"{COLOURS[reset_colour]}[{timestamp}] {new_message}{COLOURS[reset_colour]}")
    logged_amount += 1

    