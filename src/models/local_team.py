import os
import pathlib
from pathlib import Path

from datetime import date
import time

from src.models.teams_video_file_processor import TeamsVideoFileProcessor

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
            self.last_file = TeamsVideoFileProcessor(self.data.team_code + ' (' + str(self.last_index) + ').mp4', self.base_path +  self.data.team_save_location)
            self.last_date = self.last_file.get_date()
        else:
            self.last_file = None
            self.last_date = date.min

    def get_team_name(self):
        return self.data.team_name

    def add_file(self, file: TeamsVideoFileProcessor):
        if self.last_file == None:
            self.refresh_last_file()
        
        if file.get_date() > self.last_date:
            file.relocate(self.data.team_code + ' (' + str(int(self.last_index + 1)) + ').mp4', self.base_path + self.data.team_save_location)
        else:
            relocated = False
            index = self.last_index
            count = self.total_count
            next_file = self.last_file
            path = self.base_path + self.data.team_save_location
            while not relocated:
                if not next_file.get_time() > file.get_time():
                    relocate_name = next_file.filename
                    replace_name = self.data.team_code + ' (' + str(index) + '.' + str(count) + ').mp4'
                    next_file.relocate(replace_name, path)
                    file.relocate(relocate_name, path)
                    relocated = True
                else:
                    count -= 1
                    next_file = TeamsVideoFileProcessor(self.data.team_code + ' (' + str(index) + '.' + str(count) + ').mp4', path)
                
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

        return possibles

    def start_check_for_downloads(self):
        if not any( a > 0 for a in self.checked_teams.values()):
            return False
        
        downloads = [Path(self.base_download_path + "\\" +f) for f in os.listdir(self.base_download_path) if f.endswith(".mp4") and Path(self.base_download_path + "\\" + f).stat().st_ctime >= self.start_time]

        if not len(downloads) > 0:
            time.sleep(5)
            return True
            
        TeamsVideoFileProcessors = [TeamsVideoFileProcessor(file.name, self.base_download_path) for file in downloads]

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

            greatest.add_file(processor)
            self.checked_teams[greatest.get_team_name()] -= 1

        return True
