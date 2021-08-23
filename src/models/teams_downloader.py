import time
from datetime import datetime, date

from threading import Thread
from collections import deque
import os

from src.models.local_team import LocalTeam, LocalTeamManager
from src.models.browser import Browser

class TeamsAutoDownloader:
    def __init__(self, email, password, base_download_path, base_save_path, local_teams_config):
        self.email = email
        self.password = password
        self.base_download_path = base_download_path
        self.base_save_path = base_save_path
        self.local_teams_config = local_teams_config
        self.browserqueue = deque()
        self.localqueue = deque()
        self.BrowserThread = None
        self.LocalThread = None
        self.main()

    def run_browser_thread(self):
        while len(self.browserqueue) > 0:        
            op = self.browserqueue.popleft()
            print("browser", op)
            if op[0] == 0:
                self.msteams = Browser(self.email, self.password, self.base_download_path)
            elif op[0] == 1:
                if self.LocalTeamsManager.wait_untill_completed == True:
                    self.enqueue_browser_queue(op)
                else:
                    downloads = self.msteams.check_for_downloads(op[1][0], op[1][1])
                    if op[1][2] == True:
                        if downloads[op[1][0]] > 0:
                            self.LocalTeamsManager.wait_untill_completed = True
                    self.LocalTeamsManager.set_downloads(downloads)
                    
                if not self.localqueue.__contains__((1,None)):
                    self.enqueue_local_queue((1,None))
        

    def run_local_thread(self):
        while len(self.localqueue) > 0:
            op = self.localqueue.popleft()
            print("local",op)
            if op[0] == 0:
                self.LocalTeamsManager = LocalTeamManager(self.base_download_path, self.base_save_path, self.local_teams_config, time.time())
                for team in self.LocalTeamsManager.get_list_local_teams():
                    team.refresh_last_file()
                    self.enqueue_browser_queue((1, (team.get_team_name(), team.last_date, team.get_wait_untill_completed_property())))
            elif op[0] == 1:
                state = self.LocalTeamsManager.start_check_for_downloads()
                if state and not self.localqueue.__contains__((1,None)):
                    self.enqueue_local_queue((1,None))


    def enqueue_browser_queue(self, element):
        self.browserqueue.append(element)
        print(element)
        if self.BrowserThread == None or not self.BrowserThread.is_alive():
            self.BrowserThread = Thread(target=self.run_browser_thread)
            self.BrowserThread.start()

    def enqueue_local_queue(self, element):
        self.localqueue.append(element)
        if self.LocalThread == None or not self.LocalThread.is_alive():
            self.LocalThread = Thread(target=self.run_local_thread)
            self.LocalThread.start()

    def main(self):
        self.enqueue_browser_queue((0,None))
        self.enqueue_local_queue((0,None))
        