import ast
import websockets
import asyncio
import json
import logging
import sys

logger = logging.getLogger()
logger.setLevel("INFO")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

config = {
  "host_address": "0.0.0.0",
  "host_port": "7890"
}

async def listen():
  host_address = config['host_address']
  host_port = config['host_port']
  url = f"ws://0.0.0.0:7890"

  async with websockets.connect(url, ping_interval=None) as ws:
    while True:
      msg = await ws.recv()
      logger.info("%s", msg[1:-1].encode('utf-8').decode('unicode-escape'))

asyncio.get_event_loop().run_until_complete(listen())