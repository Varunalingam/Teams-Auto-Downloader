from src.models.teams_video_file_processor import TeamsVideoFileProcessor
from src.helpers.file_helper import save_cache, load_json
import sys
from os import listdir
from src.models.teams_video_file_processor import TeamsVideoFileProcessor
dir = sys.path[0]

config = load_json('data.json', dir)
cache = {}

for team in config.local_teams_config:
    if team.team_name not in cache.keys():
        cache[team.team_name] = []
    TeamsVideoFileProcessors = [TeamsVideoFileProcessor.create(file, config.base_save_path + team.team_save_location) for file in listdir(config.base_save_path + team.team_save_location) if file.endswith(".mp4")]

    for processor in TeamsVideoFileProcessors:
        cache[team.team_name].append({"size" : str(processor.get_file_size()), "length" : str(processor.get_video_length()), "time" : str(processor.get_time())})
        print("Processed file : " +  processor.filename)

save_cache(dir, cache)