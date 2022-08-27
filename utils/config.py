import json

def get_config():
  config = load_json('config.json')
  return config

def load_json(path):
  f = open(path)
  loaded = json.load(f)
  f.close()
  return loaded