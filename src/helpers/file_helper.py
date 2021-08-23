import json
import os
from types import SimpleNamespace

def load_json(filename, base_path, as_dict = False):
    config = None
    if os.path.exists(base_path + "\\" + filename):
        with open(base_path + "\\" +filename) as json_data_file:
            if not as_dict:
                config = json.loads(json_data_file.read(), object_hook=lambda d: SimpleNamespace(**d))
            else:
                config = json.load(json_data_file)
            json_data_file.close()
    return config

def del_file(filename, base_path):
    if os.path.exists(base_path + "\\" + filename):
        os.remove(base_path + "\\" + filename)

def save_data_as_json(filename, base_path, data):
    with open(base_path + "\\" + filename, 'w+') as json_file:
        json.dump(data, json_file)
        json_file.close()


def load_cache(base_path):
    return load_json("cache.json", base_path, as_dict=True)

def save_cache(base_path, updated_cache_data):
    save_data_as_json("cache.json", base_path, updated_cache_data)