import os
import pathlib
import sys
from pathlib import Path

from datetime import date
from re import S
import time

from src.models.teams_video_file_processor import TeamsVideoFileProcessor
from src.helpers.file_helper import load_cache, save_cache

class LocalTeam:
    def __init__(self, local_team, base_path):
        self.data = local_team
        self.base_path = base_path
        self.last_file = None
        self.last_date = None
        self.refresh_last_index()
    
    def refresh_last_index(self):
        target = self.data.team_code
        directory = self.base_path + self.data.team_save_location
        ls = [-1] + [int(''.join([x for x in str(file).replace('.mp4','').replace(target,'').split('.')[0] if x.isdigit()])) for file in os.listdir(directory) if str(file).__contains__(target)]
        ls = list(set(ls))
        ls.sort()
        self.last_index = ls[-1]

        if not self.last_index == -1:
            ls = [int(''.join([x for x in str(file).replace('.mp4','').replace(target,'').split('.')[1] if x.isdigit()])) for file in os.listdir(directory) if str(file).__contains__(target + ' (' + str(self.last_index) + '.')]
            ls = list(set(ls))
            self.total_count = len(ls) + 1

    def refresh_last_file(self):
        if not self.last_index == -1: 
            self.last_file = TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(self.last_index) + ').mp4', self.base_path +  self.data.team_save_location)
            self.last_date = self.last_file.get_date()
        else:
            self.last_file = None
            self.last_date = date.min

    def get_team_name(self):
        return self.data.team_name

    def get_wait_untill_completed_property(self):
        return self.data.wait_untill_completed

    def add_file(self, file: TeamsVideoFileProcessor):
        if self.last_file == None:
            self.refresh_last_file()
        
        if file.get_date() > self.last_date:
            file.relocate(self.data.team_code + ' (' + str(int(self.last_index + 1)) + ').mp4', self.base_path + self.data.team_save_location)
        else:
            index = self.last_index
            path = self.base_path + self.data.team_save_location
            target = self.data.team_code
            directory = self.base_path + self.data.team_save_location

            indexbreak = False

            while index >= 0:
                currentfile = TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(index) + ').mp4', path)
                if currentfile.get_date() == file.get_date():
                    break
                elif currentfile.get_date() > file.get_date():
                    indexbreak = True
                    break
                index -= 1
            
            if indexbreak:
                replace_index = self.last_index
                while replace_index >= index + 1:
                    ls = [int(''.join([x for x in str(file).replace('.mp4','').replace(target,'').split('.')[1] if x.isdigit()])) for file in os.listdir(directory) if str(file).__contains__(target + ' (' + str(replace_index) + '.')]
                    ls = list(set(ls))
                    current_count = len(ls) - 1
                    TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(replace_index) + ').mp4', path).relocate(self.data.team_code + ' (' + str(replace_index + 1) + ').mp4', path)
                    while current_count >= 0:
                        TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(replace_index) + '.' + str(current_count) + ').mp4', path).relocate(self.data.team_code + ' (' + str(replace_index + 1) + '.' + str(current_count) + ').mp4', path)
                        current_count -= 1
                    replace_index -= 1
                file.relocate(self.data.team_code + ' (' + str(index+1) +').mp4', path)

            elif index >= 0:
                ls = [int(''.join([x for x in str(file).replace('.mp4','').replace(target,'').split('.')[1] if x.isdigit()])) for file in os.listdir(directory) if str(file).__contains__(target + ' (' + str(self.last_index) + '.')]
                ls = list(set(ls))
                current_count = len(ls) - 1
                if TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(index) + ').mp4', path).get_time() <= file.get_time():
                    TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(index) + ').mp4', path).relocate(self.data.team_code + ' (' + str(index) + '.' + str(current_count + 1) + ').mp4' ,path)
                    file.relocate(self.data.team_code + ' (' + str(index) + ').mp4' ,path)
                else:
                    until_count = current_count
                    while current_count >= 0:
                        if file.get_time() >= TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(index) + '.' + str(current_count) + ').mp4', path).get_time():
                            break
                        current_count -= 1
                    
                    while current_count >= until_count:
                        TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(index) + '.' + str(until_count) + ').mp4', path).relocate(self.data.team_code + ' (' + str(index) + '.' + str(until_count + 1) + ').mp4', path)
                        until_count -= 1
            else:
                replace_index = self.last_index
                while replace_index >= 0:
                    ls = [int(''.join([x for x in str(file).replace('.mp4','').replace(target,'').split('.')[1] if x.isdigit()])) for file in os.listdir(directory) if str(file).__contains__(target + ' (' + str(replace_index) + '.')]
                    ls = list(set(ls))
                    current_count = len(ls) - 1
                    TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(replace_index) + ').mp4', path).relocate(self.data.team_code + ' (' + str(replace_index + 1) + ').mp4', path)
                    while current_count >= 0:
                        TeamsVideoFileProcessor.create(self.data.team_code + ' (' + str(replace_index) + '.' + str(current_count) + ').mp4', path).relocate(self.data.team_code + ' (' + str(replace_index + 1) + '.' + str(current_count) + ').mp4', path)
                        current_count -= 1
                    replace_index -= 1
                file.relocate(self.data.team_code + ' (0).mp4', path)
                
        self.refresh_last_index()
        self.refresh_last_file()

    def get_mandatory_matching_quotient(self, file: TeamsVideoFileProcessor):
        match = 0
        match_factor = 0
        if self.data.mandatory_conditions.min_time > 0:
            match_factor += 1
            if file.get_video_length() > int(self.data.mandatory_conditions.min_time * 60):
                match += 1
        if self.data.mandatory_conditions.max_time > 0:
            match_factor += 1
            if file.get_video_length() < int(self.data.mandatory_conditions.max_time * 60):
                match += 1
        match_factor += 1 if len(self.data.mandatory_conditions.days) > 0 else 0
        for day in self.data.mandatory_conditions.days:
            if int(file.get_time().weekday()) == int(day):
                match += 1
                break
        match_factor += 1 if len(self.data.mandatory_conditions.strings) > 0 else 0
        text_match = 0
        text_match_factor = len(file.get_processed_data())
        for text in file.get_processed_data():
            if any (phrase.lower() in text.lower() for phrase in self.data.mandatory_conditions.strings):
                text_match += 1
        match += float(text_match)/float(text_match_factor)
        if match_factor > 0:
            return float((float(match)/match_factor) - 0.5)
        return 0

    def get_matching_quotient(self, file: TeamsVideoFileProcessor):
        match = 0
        match_factor = 0
        if self.data.matching_conditions.min_time > 0:
            match_factor += 1
            if file.get_video_length() > int(self.data.matching_conditions.min_time * 60):
                match += 1
        if self.data.matching_conditions.max_time > 0:
            match_factor += 1
            if file.get_video_length() < int(self.data.matching_conditions.max_time * 60):
                match += 1
        match_factor += 1 if len(self.data.matching_conditions.days) > 0 else 0
        for day in self.data.matching_conditions.days:
            if int(file.get_time().weekday()) == int(day):
                match += 1
                break
        match_factor += 1 if len(self.data.matching_conditions.strings) > 0 else 0
        text_match = 0
        text_match_factor = len(file.get_processed_data())
        for text in file.get_processed_data():
            if any (phrase.lower() in text.lower() for phrase in self.data.matching_conditions.strings):
                text_match += 1
        match += float(text_match)/float(text_match_factor)
        if match_factor > 0:
            return float((float(match)/match_factor))
        return 0

class LocalTeamManager:
    def __init__(self, base_download_path, base_save_path, local_teams_config, start_time):
        self.base_download_path = base_download_path
        self.base_save_path = base_save_path
        self.create_local_teams(local_teams_config)
        self.checked_teams = {}
        self.start_time = start_time
        self.wait_untill_completed = False
        self.cache_data = {}
        self.get_cache_data()

    def get_cache_data(self):
        dir = sys.path[0]
        self.cache_data = load_cache(dir)

    def check_for_match(self, team_name, file: TeamsVideoFileProcessor):
        for a in self.cache_data[team_name]:
            if a["size"] == str(file.get_file_size()):
                if a["length"] == str(file.get_video_length()):
                    if a["time"] == str(file.get_time()):
                        return True
        return False

    def update_cache(self, file: TeamsVideoFileProcessor, team_name):
        self.cache_data[team_name].append({"size" : str(file.get_file_size()), "length" : str(file.get_video_length()), "time" : str(file.get_time())})
        dir = sys.path[0]
        save_cache(dir,self.cache_data)
        

    def create_local_teams(self, local_teams_config):
        self.LocalTeams = {}
        for team in local_teams_config:
            try:
                os.makedirs(self.base_save_path + "\\" + team.team_save_location)
            except:
                pass
            if not team.team_name in self.LocalTeams.keys():
                self.LocalTeams[team.team_name] = []
            self.LocalTeams[team.team_name] += [LocalTeam(team, self.base_save_path)]
        print(self.LocalTeams)

    def get_list_local_teams(self):
        out = []
        for value in self.LocalTeams.values():
            out += value
        return out 

    def set_downloads(self, checked_teams):
        for key in checked_teams:
            if not key in self.checked_teams.keys():
                self.checked_teams[key] = checked_teams[key]

    def get_possible_matches(self):
        possibles = []
        for key in self.checked_teams:
            if self.checked_teams[key] > 0:
                possibles += self.LocalTeams[key]
        print(possibles, self.checked_teams)
        return possibles

    def start_check_for_downloads(self):
        if not any( a > 0 for a in self.checked_teams.values()):
            return False
        
        downloads = [Path(self.base_download_path + "\\" +f) for f in os.listdir(self.base_download_path) if f.endswith(".mp4") and Path(self.base_download_path + "\\" + f).stat().st_ctime >= self.start_time]

        if not len(downloads) > 0:
            time.sleep(5)
            return True
            
        TeamsVideoFileProcessors = [TeamsVideoFileProcessor.create(file.name, self.base_download_path) for file in downloads]

        for processor in TeamsVideoFileProcessors:
            match_q = {}
            possibles = self.get_possible_matches()
            greatest = possibles[0]
            if len(possibles) > 1:
                for localTeam in possibles:
                    match_q[localTeam] = (2 * localTeam.get_mandatory_matching_quotient(processor)) + localTeam.get_matching_quotient(processor)
                
                greatest = None
                for key in match_q.keys():
                    if greatest == None:
                        greatest = key
                    
                    if match_q[key] > match_q[greatest]:
                        greatest = key

            if not self.check_for_match(greatest.get_team_name(), processor):
                greatest.add_file(processor)
                self.update_cache(processor, greatest.get_team_name())
            else:
                TeamsVideoFileProcessor.delete(processor)
                
            self.checked_teams[greatest.get_team_name()] -= 1

            if self.wait_untill_completed == True and greatest.get_wait_untill_completed_property() and self.checked_teams[greatest.get_team_name()] <= 0:
                self.wait_untill_completed = False

        return True
