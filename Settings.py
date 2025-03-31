import json
import os

# default settings if not settings.json file
default_data = {
    "token": "",
    "bot_username": "@",
    "chat_id": 0,
    "cooldown": 30,

    "cam_height": 720,
    "cam_width": 1280,

    "record_interval": 60,

    "zone_y1": 0,
    "zone_y2": 720,
    "zone_x1": 0,
    "zone_x2": 1280,

    "buffer": 15,
    "GIF_notification": 1
    }

# load settings file. Creates and uses default settings above if file not found
def load(filename="settings.json"):
    if not os.path.exists(filename):
        with open(filename,"w") as file:
            json.dump(default_data,file)

    with open(filename, "r") as file:
        return json.load(file)

# load settings file on program run
settings = load()