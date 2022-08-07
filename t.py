import os, sys
import argparse
import subprocess

arguments = argparse.ArgumentParser()
arguments.add_argument("-i", "--id", dest="id", help="content id ")
arguments.add_argument("-o", "--Name", dest="Name", help="quality") 
args = arguments.parse_args()

 
def trackname():
     link = str(args.id) 
     os.system('ffmpeg -i %s -map 0:v -map 0:a -map 0:s? -metadata title="@TROOPORIGINALS" -metadata:s:v title="TroopOriginals" -metadata:s:a title="TroopOriginals" -metadata:s:s title="TroopOriginals" -codec copy %s'%(link,filename))
     output = f"'{filename}'"
     subprocess.run(['rclone','move',output,'Rose:'])

filename = str(args.Name)
trackname()
