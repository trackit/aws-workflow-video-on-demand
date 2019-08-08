import os
import json

path = './config.json'

conf = None

def read_conf():
    global conf
    if conf is None:
        if os.path.isfile(path):
            with open(path) as raw:
                conf = json.load(raw)
                return conf
        else:
            return None
    return conf

def get_config(*args):
    data = read_conf()
    for arg in args:
        if arg in data:
            data = data[arg]
        else:
            return None
    return data
