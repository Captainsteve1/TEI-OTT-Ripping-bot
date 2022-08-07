#!/usr/bin/env python3

import os 
import subprocess
import shutil
import glob
import pathlib
import platform
import time
import argparse


FILE_DIRECTORY=str(pathlib.Path(__file__).parent.absolute())
TEMPORARY_PATH = FILE_DIRECTORY+"/cache"
OUTPUT_PATH = FILE_DIRECTORY+"/output"
ENCODES = FILE_DIRECTORY+"/encodes"
SUBTITLES = FILE_DIRECTORY+"/subtitles"


arguments = argparse.ArgumentParser()
arguments.add_argument("-l", "--mpd", dest="mpd", help="mpd link")
arguments.add_argument("-k","--keys", dest="key",  help="key")
arguments.add_argument("-o", "--output", dest="output", help="File Name")

args = arguments.parse_args()

def osinfo():
	global PLATFORM
	if platform.system()== "Darwin":
		PLATFORM = "Mac"
	else:
		PLATFORM = platform.system()
		
def divider():
	print ('-' * shutil.get_terminal_size().columns)
	
def empty_folder(folder):
	files = glob.glob('%s/*'%folder)
	for f in files:
		os.remove(f)
	quit()
	
def extract_key (prompt):
	global key,kid,keys
	key = prompt[30 : 62]
	kid = prompt[68 : 100]
	keys = args.key
	return key,kid,keys

def permit():
    os.system('chmod u+x mp4decrypt/mp4decrypt')


def download_drm_content(mpd_url):
	divider()
	print("Processing Video Info..")
	os.system('yt-dlp --external-downloader aria2c --no-warnings --allow-unplayable-formats --no-check-certificate -F "%s"'%mpd_url)
	divider()
	VIDEO_ID = input("ENTER VIDEO_ID (Press Enter for Best): ")
	if VIDEO_ID == "":
		VIDEO_ID = "bv"
	
	AUDIO_ID = input("ENTER AUDIO_ID (Press Enter for Best): ")
	if AUDIO_ID == "":
		AUDIO_ID = "ba"
	
	divider()
	print("Downloading Encrypted Video from CDN..")	
	os.system(f'yt-dlp -o "{TEMPORARY_PATH}/encrypted_video.%(ext)s" --no-warnings --external-downloader aria2c -r 10M --allow-unplayable-formats --no-check-certificate -f {VIDEO_ID} "{mpd_url}" -o "{TEMPORARY_PATH}/encrypted_video.%(ext)s"')
	print("Downloading Encrypted Audio from CDN..")
	os.system(f'yt-dlp -o "{TEMPORARY_PATH}/encrypted_audio.%(ext)s" --no-warnings --external-downloader aria2c -r 10M --allow-unplayable-formats --no-check-certificate -f {AUDIO_ID} "{mpd_url}"')

def decrypt_content():
	extract_key(KEY_PROMPT)
	divider()
	print("Decrypting WideVine DRM.. (Takes some time)")
	osinfo()
	if PLATFORM == "Mac":
		MP4DECRYPT_PATH = "%s/mp4decrypt/mp4decrypt_mac"%FILE_DIRECTORY
	elif PLATFORM == "Windows":
		MP4DECRYPT_PATH = "%s/mp4decrypt/mp4decrypt_win.exe"%FILE_DIRECTORY
	elif PLATFORM == "Linux":
		MP4DECRYPT_PATH = "%s/mp4decrypt/mp4decrypt"%FILE_DIRECTORY
	else:
		MP4DECRYPT_PATH = MP4DECRYPT_PATH = "mp4decrypt"
		
	os.system('%s %s/encrypted_video.mp4 %s/decrypted_video.mp4 --key %s --show-progress'%(MP4DECRYPT_PATH,TEMPORARY_PATH,TEMPORARY_PATH,keys))
	os.system('%s %s/encrypted_audio.m4a %s/decrypted_audio.m4a --key %s --show-progress'%(MP4DECRYPT_PATH,TEMPORARY_PATH,TEMPORARY_PATH,keys))
	print("Decryption Complete!")

def merge_content():
	divider()
	FILENAME= str(args.output)
	divider()
	print("Merging Files and Processing %s.. (Takes a while)"%FILENAME)
	time.sleep(2)
	os.system('ffmpeg -i %s/decrypted_video.mp4 -i %s/decrypted_audio.m4a -i %s/decrypted_subs.en.srt -preset ultrafast -hide_banner -c:v copy -c:a copy -c:s copy %s/%s'%(TEMPORARY_PATH,TEMPORARY_PATH,OUTPUT_PATH,OUTPUT_PATH,FILENAME))

def trackname():
        divider()
        FILENAME= str(args.output)
        os.system('ffmpeg -i %s/%s -hide_banner -map 0:v -map 0:a -map 0:s? -metadata title="TroopOriginals" -metadata:s:v title="TroopOriginals" -metadata:s:a title="TroopOriginals" -metadata:s:s title="TroopOriginals" -codec copy %s/thelidhu.mkv && mv %s/thelidhu.mkv %s/%s'%(OUTPUT_PATH,FILENAME,OUTPUT_PATH,OUTPUT_PATH,ENCODES,FILENAME))

def watermark():
        FILENAME= str(args.output)
        os.system('ffmpeg -i %s/%s -i troop.png -preset ultrafast -filter_complex "[0:v][1:v] overlay=25:25:enable=between(t\,0\,10)" %s/%s'%(OUTPUT_PATH,FILENAME,ENCODES,FILENAME))

def subtitles(mpd_url):
    print("Downloading Subtitles")
    os.system(f'yt-dlp --write-subs --convert-sub srt --sub-lang en --skip-download --external-downloader aria2c --verbose --allow-u "%s" -o %s/decrypted_subs'%(mpd_url,OUTPUT_PATH))

def rclone():
    print("Aagu Ra Nakka Pumka")
    FILENAME = args.output
    output =  ENCODES + '/' + f"{FILENAME}"
    print(output)
    subprocess.run(['rclone','copy', output,'Rose:/webdl'])

divider()
print("**** Aagu Ra Nakka Pumka ****")
divider()
MPD_URL = str(args.mpd)
KEY_PROMPT = str(args.key)
download_drm_content(MPD_URL)
subtitles(MPD_URL)
decrypt_content()
merge_content()
trackname()
rclone()
divider()
print("drive folder lo vethuko ugga :- https://drive.google.com/drive/folders/1fTLc6LSBZ2txSgeMy2xgKgYcJu4iyc1Y?usp=sharing")
divider()

empty_folder(TEMPORARY_PATH)

	
