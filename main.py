import sys

from src.models.teams_downloader import TeamsAutoDownloader
from src.helpers.file_helper import load_json, del_file

dir = sys.path[0]
del_file('cache.json', dir)

config = load_json('data.json', dir)

TeamsAutoDownloader(config.email, config.password, config.base_download_path, config.base_save_path, config.local_teams_config)
