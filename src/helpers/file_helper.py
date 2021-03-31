import json
import os
from types import SimpleNamespace

def load_json(filename, base_path):
    config = None
    if os.path.exists(base_path + "\\" + filename):
        with open(base_path + "\\" +filename) as json_data_file:
            config = json.loads(json_data_file.read(), object_hook=lambda d: SimpleNamespace(**d))
            json_data_file.close()
    return config

def del_file(filename, base_path):
    if os.path.exists(base_path + "\\" + filename):
        os.remove(base_path + "\\" + filename)

def save_data_as_json(filename, base_path, data):
    with open(base_path + "\\" + filename, 'w+') as json_file:
        json.dump(data, json_file)
        json_file.close()
