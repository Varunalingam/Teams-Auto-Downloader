from src.models.local_team import LocalTeam
import os
import pathlib
from src.models.teams_video_file_processor import TeamsVideoFileProcessor
from src.helpers.file_helper import load_json
import sys


dir = sys.path[0]
config = load_json('data.json', dir)

b = LocalTeam(config.local_teams_config[2], "C:\\Users\\varun\\Google Drive (icea.2023.nitt@gmail.com)\\ICE-A 23'\\Video Lectures\\Sem 4")
a = LocalTeam(config.local_teams_config[-1], "C:\\Users\\varun\\Google Drive (icea.2023.nitt@gmail.com)\\ICE-A 23'\\Video Lectures\\Sem 4")

z = [TeamsVideoFileProcessor.create(str(f), "C:\\Users\\varun\\Google Drive (icea.2023.nitt@gmail.com)\\ICE-A 23'\\Video Lectures\\Sem 4" + "\\Labs\\ICLR13 - Analog Signal Processing Laboratory") for f in os.listdir("C:\\Users\\varun\\Google Drive (icea.2023.nitt@gmail.com)\\ICE-A 23'\\Video Lectures\\Sem 4" + "\\Labs\\ICLR13 - Analog Signal Processing Laboratory") if str(f).endswith('.mp4')]
z += [TeamsVideoFileProcessor.create(str(f), "C:\\Users\\varun\\Google Drive (icea.2023.nitt@gmail.com)\\ICE-A 23'\\Video Lectures\\Sem 4" + "\\PC & GIR's\\ICPC17 - Analog Signal Processing") for f in os.listdir("C:\\Users\\varun\\Google Drive (icea.2023.nitt@gmail.com)\\ICE-A 23'\\Video Lectures\\Sem 4" + "\\PC & GIR's\\ICPC17 - Analog Signal Processing") if str(f).endswith('.mp4')]

for zs in z:
    print(zs.filename)
    print(zs.get_video_length())
    print( "Lab :Mandatory Quotient {} , Matching Quotient {}".format(a.get_mandatory_matching_quotient(zs), a.get_matching_quotient(zs)))
    print( "Theory :Mandatory Quotient {} , Matching Quotient {}".format(b.get_mandatory_matching_quotient(zs), b.get_matching_quotient(zs)))
    