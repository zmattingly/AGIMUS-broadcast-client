import asyncio
import colorsys
import logging
import re
import requests
import sys
import websockets

from huesdk import Hue
from nanoleafapi import Nanoleaf
from pprint import pprint
from PIL import ImageColor
from urllib3.exceptions import InsecureRequestWarning

from utils.config import get_config

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logger = logging.getLogger()
logger.setLevel("INFO")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

config = get_config()

#   ___ ___
#  /   |   \ __ __   ____
# /    ~    \  |  \_/ __ \
# \    Y    /  |  /\  ___/
#  \___|_  /|____/  \___  >
#        \/             \/
hue = Hue(
  bridge_ip=config['hue']['bridge_ip'],
  username=config['hue']['username']
)
light = hue.get_light(name=config['hue']['target_light_name'])
light.set_saturation(254)


#  _______                       .__                 _____
#  \      \ _____    ____   ____ |  |   ____ _____ _/ ____\
#  /   |   \\__  \  /    \ /  _ \|  | _/ __ \\__  \\   __\
# /    |    \/ __ \|   |  (  <_> )  |_\  ___/ / __ \|  |
# \____|__  (____  /___|  /\____/|____/\___  >____  /__|
#         \/     \/     \/                 \/     \/
nl = Nanoleaf("192.168.1.153")

def activate_nanoleaf_panel(hex):
  scene = "Cocoa Beach"
  if hex == "40999b":
    scene = "Cyan Burst"
  if hex == "ed61e6":
    scene = "Purple Flow"
  if hex == "3465a4" or hex == "75507b":
    scene = "Blue Flow"
  if hex == "a449a6":
    scene = "Violet Burst"
  if hex == "cd3b28":
    scene = "Red Wheel"
  if hex == "d06265":
    scene = "Pink Burst"
  if hex == "c4a124" or hex == "e1e500":
    scene = "Yellow Wheel"
  if hex == "4e9a09":
    scene = "Green Flow"
  if hex == "00f592" or hex == "00f8ff":
    scene = "Cyan Burst"

  nl.set_effect(scene)


# def generate_nanoleaf_effect(name, anim_type, hsl):
#   print(f"hsl: {hsl}")
#   base_h = int(hsl[0]),
#   base_h = base_h[0]
#   base_s = int(hsl[1])
#   base_l = int(hsl[2])

#   print(base_h)
#   print(base_s)
#   print(base_l)

#   base_hsl = (base_h, base_s, base_l)
#   lower_hsl = (base_h, base_s, base_l)
#   upper_hsl = (base_h, base_s, base_l)

#   effect_data = {
#     "command": "display",
#     "animName": name,
#     "animType": anim_type,
#     "colorType": "HSB",
#     "animData": None,
#     "palette": [
#       {
#         "hue": lower_hsl[0],
#         "saturation": lower_hsl[1],
#         "brightness": lower_hsl[2]
#       },
#       {
#         "hue": base_hsl[0],
#         "saturation": base_hsl[1],
#         "brightness": base_hsl[2]
#       },
#       {
#         "hue": upper_hsl[0],
#         "saturation": upper_hsl[1],
#         "brightness": upper_hsl[2]
#       }
#     ],
#     "brightnessRange": {
#       "minValue": 50,
#       "maxValue": 100
#     },
#     "transTime": {
#       "minValue": 50,
#       "maxValue": 100
#     },
#     "delayTime": {
#       "minValue": 50,
#       "maxValue": 100
#     },
#     "loop": True
#   }

#   pprint(effect_data)
#   nl.write_effect(effect_data)
#   pprint(nl.list_effects())

def get_rgb_from_hex(hex):
  stripped_hex = hex.lstrip("#")
  hex = f"#{stripped_hex}"
  return ImageColor.getcolor(hex.upper(), "RGB")

def get_hsl_from_rgb(rgb):
  r = rgb[0]
  g = rgb[1]
  b = rgb[2]
  return colorsys.rgb_to_hls(r, g, b)


#    _____    _______    _________.___
#   /  _  \   \      \  /   _____/|   |
#  /  /_\  \  /   |   \ \_____  \ |   |
# /    |    \/    |    \/        \|   |
# \____|__  /\____|__  /_______  /|___|
#         \/         \/        \/
split_ANSI_escape_sequences = re.compile(r"""
  (?P<col>(\x1b # literal ESC
  \[            # literal [
  [;\d]*        # zero or more digits or semicolons
  [A-Za-z]      # a letter
  )*)
  (?P<name>.*)
  """, re.VERBOSE).match

def split_ANSI(s):
  return split_ANSI_escape_sequences(s).groupdict()


# _________        .__
# \_   ___ \  ____ |  |   ___________
# /    \  \/ /  _ \|  |  /  _ \_  __ \
# \     \___(  <_> )  |_(  <_> )  | \/
#  \______  /\____/|____/\____/|__|
#         \/
LOW_TO_RGB = {
  "30": (46, 52, 55),    # Grey
  "31": (205, 59, 40),   # Red
  "32": (78, 154, 9),    # Green
  "33": (196, 161, 36),  # Yellow
  "34": (52, 101, 164),  # Blue
  "35": (117, 80, 123),  # Magenta
  "36": (64, 153, 155),  # Cyan
  "37": (211, 215, 207), # Reset
  "38": (211, 215, 207), # Reset
  "39": (211, 215, 207), # Reset
}

HIGH_TO_RGB = {
  "92": (208, 98, 101),  # Light Red
  "93": (0, 245, 146),   # Light Green
  "94": (225, 229, 0),   # Light Yellow
  "95": (153, 149, 210), # Light Blue
  "95": (237, 97, 230),  # Magenta
  "96": (164, 73, 166),  # Light Magenta
  "97": (0, 248, 255)    # Light Cyan
}

def get_hex_from_logline(msg):
  split = split_ANSI(msg)
  col = split.get("col")
  if not col:
    return "#dddddd"

  ansi_matches = re.findall(r"(\d+)m", col)
  ansi_number = 0
  for match in ansi_matches:
    ansi_number += int(match)
    if ansi_number >= 30 and ansi_number <= 39:
      break

  hex = _get_hex_from_ansi(ansi_number)
  return hex

def _get_hex_from_ansi(ansi):
  ansi = int(ansi)
  if ansi >= 30 and ansi <= 39:
    rgb = LOW_TO_RGB.get(str(ansi))
  else:
    rgb = HIGH_TO_RGB.get(str(ansi))

  if rgb is None:
    rgb = (211, 215, 207)

  return _get_hex_from_rgb(rgb)

def _get_hex_from_rgb(rgb):
  return '%02x%02x%02x' % rgb


#  __      __      ___.                        __           __
# /  \    /  \ ____\_ |__   __________   ____ |  | __ _____/  |_  ______
# \   \/\/   // __ \| __ \ /  ___/  _ \_/ ___\|  |/ // __ \   __\/  ___/
#  \        /\  ___/| \_\ \\___ (  <_> )  \___|    <\  ___/|  |  \___ \
#   \__/\  /  \___  >___  /____  >____/ \___  >__|_ \\___  >__| /____  >
#        \/       \/    \/     \/           \/     \/    \/          \/
async def listen():
  host_address = config['host']['host_address']
  host_port = config['host']['host_port']
  url = f"ws://{host_address}:{host_port}"

  async with websockets.connect(url, ping_timeout=None) as ws:
    while True:
      msg = await ws.recv()
      formatted_msg = msg[1:-1].encode('raw_unicode_escape').decode('unicode-escape').encode('utf-16_BE','surrogatepass').decode('utf-16_BE')
      try:
        logger.info("%s", formatted_msg)
      except Exception as e:
        pass

      hex = get_hex_from_logline(formatted_msg)
      if light.is_on:
        light.set_color(hexa=hex, transition=3)
      if nl.get_power():
        activate_nanoleaf_panel(hex)


asyncio.get_event_loop().run_until_complete(listen())
