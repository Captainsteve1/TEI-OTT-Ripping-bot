import os
import json
import subprocess
import argparse
import sys
import pyfiglet
from rich import print
from typing import DefaultDict


print("Tej WEB-DL BOT")

arguments = argparse.ArgumentParser()
arguments.add_argument("-m", "--video-link", dest="mpd", help="MPD url")
arguments.add_argument("-k","--key",dest=keys,help="keys")
arguments.add_argument("-o", '--output', dest="output", help="Specify output file name with no extension", required=True)
arguments.add_argument("-id", dest="id", action='store_true', help="use if you want to manually enter video and audio id.")
arguments.add_argument("-s", dest="subtitle", help="enter subtitle url")
args = arguments.parse_args()

currentFile = __file__
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
dirName = os.path.basename(dirPath)

youtubedlexe = 'yt-dlp'
aria2cexe = '/usr/src/app/bin/tools/aria2c'
mp4decryptexe = '/usr/src/app/bin/tools/mp4decrypt'
mkvmergeexe = '/usr/src/app/bin/tools/mkvmerge'
SubtitleEditexe = 'SubtitleEdit'

keys = str(args.keys)
mpdurl = str(args.mpd)
output = str(args.output)
subtitle = str(args.subtitle)

if args.id:    
    subprocess.run([youtubedlexe, '-k', '--allow-unplayable-formats', '--no-check-certificate', '-F', json_mpd_url])

    vid_id = input("\nEnter Video ID : ")
    audio_id = input("Enter Audio ID : ")
    subprocess.run([youtubedlexe, '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', audio_id, '--fixup', 'never', json_mpd_url, '-o', 'encrypted.m4a', '--external-downloader', aria2cexe, '--external-downloader-args', '-x 16 -s 16 -k 1M'])
    subprocess.run([youtubedlexe, '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', vid_id, '--fixup', 'never', json_mpd_url, '-o', 'encrypted.mp4', '--external-downloader', aria2cexe, '--external-downloader-args', '-x 16 -s 16 -k 1M'])   

else:
    subprocess.run([youtubedlexe, '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', 'ba', '--fixup', 'never', mpd_url, '-o', 'encrypted.m4a','--external-downloader-args', '-x 16 -s 16 -k 1M'])
    subprocess.run([youtubedlexe, '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', 'bv', '--fixup', 'never', mpd_url, '-o', 'encrypted.mp4','--external-downloader-args', '-x 16 -s 16 -k 1M'])    


print("\nDecrypting .....")
subprocess.run(f'{mp4decryptexe} --show-progress {keys} encrypted.m4a decrypted.m4a', shell=True)
subprocess.run(f'{mp4decryptexe} --show-progress {keys} encrypted.mp4 decrypted.mp4', shell=True)  

if args.subtitle:
    subprocess.run(f'{aria2cexe} {subtitle}', shell=True)
    os.system('ren *.xml en.xml')
    subprocess.run(f'{SubtitleEditexe} /convert en.xml srt', shell=True) 
    print("Merging .....")
    subprocess.run([mkvmergeexe, '--ui-language' ,'en', '--output', output +'.mkv', '--language', '0:eng', "--track-name","0:Tele_Pirate",'--default-track', '0:yes', '--compression', '0:none', 'decrypted.mp4', '--language', '0:eng',"--track-name","1:Tele_Pirate", '--default-track', '0:yes', '--compression' ,'0:none', 'decrypted.m4a','--language', '0:eng',"--track-name","2:Tele_Pirate",'--track-order', '0:0,1:0,2:0,3:0,4:0', 'en.srt'])
    print("\nAll Done .....")
else:
    print("Merging .....")
    subprocess.run([mkvmergeexe, '--ui-language' ,'en', '--output', output +'.mkv', '--language', '0:eng',"--track-name","0:Tele_Pirate", '--default-track', '0:yes', '--compression', '0:none', 'decrypted.mp4', '--language', '0:eng',"--track-name","1:Tele_Pirate", '--default-track', '0:yes', '--compression' ,'0:none', 'decrypted.m4a','--language', '0:eng','--track-order', '0:0,1:0,2:0,3:0,4:0'])
    print("\nAll Done .....")    

print("\nDo you want to delete the Encrypted Files : Press 1 for yes , 2 for no")
delete_choice = int(input("Enter Response : "))

if delete_choice == 1:
    os.remove("encrypted.m4a")
    os.remove("encrypted.mp4")
    os.remove("decrypted.m4a")
    os.remove("decrypted.mp4")
    try:    
        os.remove("en.srt")
    except:
        pass
else:
    pass
