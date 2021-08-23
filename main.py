import sys

from src.models.teams_downloader import TeamsAutoDownloader
from src.helpers.file_helper import load_json, load_cache

dir = sys.path[0]

config = load_json('data.json', dir)

if len(dict(load_cache(dir)).keys()) != len(config.local_teams_config):
    import cache_generator

TeamsAutoDownloader(config.email, config.password, config.base_download_path, config.base_save_path, config.local_teams_config)
