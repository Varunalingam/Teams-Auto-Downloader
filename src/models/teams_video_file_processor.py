import pathlib
from datetime import datetime, timedelta
import sys
import os

from src.helpers.textRecognition import textFromVideo, videoLength
from src.helpers.file_helper import load_json, save_data_as_json

class TeamsVideoFileProcessor:
    def __init__(self, filename, base_path):
        if not str(filename).endswith('.mp4'):
            filename += '.mp4'
        self.file = pathlib.Path(base_path + "\\" + filename)
        self.data = None
        self.date = None
        self.time = None
        self.filename = filename
        self.videoLength = None
        if not self.file.exists():
            raise Exception('File Does Not Exist at path {}'.format(base_path + "\\" + filename))
    
    def create_processed_data(self):
        if self.data == None:
            dir = sys.path[0]
            if not os.path.exists(dir + '\\cache.json'):
                save_data_as_json('cache.json', dir, {})
            
            config = load_json('cache.json', dir, as_dict=True)
            
            if not str(self.file.absolute()) in config.keys():
                ret = True
                startFrame = 0
                self.data = []
                startTime = datetime.now()
                while(ret and datetime.now() - startTime < timedelta(seconds=20)):
                    ret, texts = textFromVideo(str(self.file.absolute()),['Microsoft Teams'],startFrame, startFrame + 10)
                    self.data += texts
                    startFrame += 10

                config[str(self.file.absolute())] = self.data

                save_data_as_json('cache.json',dir, config)
            else:
                self.data = config[str(self.file.absolute())]

    
    def get_processed_data(self):
        self.create_processed_data()
        return self.data
    
    def get_date(self):
        if not self.date == None:
            return self.date
        
        self.create_processed_data()

        dates = []

        for text in self.data:
            timestring = None
            for a in text.splitlines():
                if a.lower().__contains__('utc'):
                    timestring = a
                    break

            if not timestring == None:
                try:
                    dates.append(datetime(int(''.join([x for x in timestring.split('-')[0] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[1] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[2].split(' ')[0] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[2].split(' ')[1].split(':')[0] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[2].split(' ')[1].split(':')[1] if x.isdigit()]))))
                except:
                    pass
        
        matching_coeff = {}

        for date in dates:
            if date.date() in matching_coeff.keys():
                matching_coeff[date.date()] += 1
            else:
                matching_coeff[date.date()] = 1
        
        greatest = None

        for key in matching_coeff.keys(): 
            if greatest == None:
                greatest = key
            else:
                if matching_coeff[greatest] < matching_coeff[key]:
                    greatest = key

        if not greatest == None:
            self.date = greatest
        else:
            self.date = datetime.now().date()
        
        self.date = self.date.replace(year=datetime.now().date().year)

        return self.date

    def get_time(self):
        if not self.time == None:
            return self.time
        
        self.get_date()

        dates = []

        for text in self.data:
            timestring = None
            for a in text.splitlines():
                if a.lower().__contains__('utc'):
                    timestring = a
                    break

            if not timestring == None:
                try:
                    date = datetime(int(''.join([x for x in timestring.split('-')[0] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[1] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[2].split(' ')[0] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[2].split(' ')[1].split(':')[0] if x.isdigit()])), int(''.join([x for x in timestring.split('-')[2].split(' ')[1].split(':')[1] if x.isdigit()])))
                    if date.date() == self.get_date():
                        dates.append(date)
                except:
                    pass
        
        if len(dates) > 0:
            self.time = dates[-1]
        else:
            self.time = datetime.now()

        self.time = self.time.replace(year=datetime.now().date().year)
        
        return self.time

    
    def get_video_length(self):
        if self.videoLength == None:
            self.videoLength = int(videoLength(str(self.file.absolute())))
        return self.videoLength

    def relocate(self, filename, base_path):
        if not str(filename).endswith('.mp4'):
            filename += '.mp4'
        try:
            self.file.rename(base_path + '\\' +  filename)
            self.filename = filename
            self.file = pathlib.Path(base_path+ '\\' + self.filename)
        except Exception as e:
            return e
        return None
