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
	print("Emptied Temporary Files!")
	divider()
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
	os.system(f'yt-dlp -o "{TEMPORARY_PATH}/encrypted_video.%(ext)s" --no-warnings --allow-unplayable-formats --no-check-certificate -f {VIDEO_ID} "{mpd_url}" -o "{TEMPORARY_PATH}/encrypted_video.%(ext)s"')
	print("Downloading Encrypted Audio from CDN..")
	os.system(f'yt-dlp -o "{TEMPORARY_PATH}/encrypted_audio.%(ext)s" --no-warnings --allow-unplayable-formats --no-check-certificate -f {AUDIO_ID} "{mpd_url}"')


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
	os.system('ffmpeg -i %s/decrypted_video.mp4 -i %s/decrypted_audio.m4a -c:v copy -c:a copy %s/%s'%(TEMPORARY_PATH,TEMPORARY_PATH,OUTPUT_PATH,FILENAME))
def rclone():
    print("Uploading Gdrive..[Rclone]")
    FILENAME = args.output
    output =  OUTPUT_PATH + '/' + f"{FILENAME}"
    print(output)
    subprocess.run(['rclone','copy', output,'Rose:/Webdl'])


divider()
print("**** Troop dl BOT****")
divider()
MPD_URL = str(args.mpd)
KEY_PROMPT = str(args.key)
permit()
download_drm_content(MPD_URL)
decrypt_content()
merge_content()
rclone()
divider()
print("Process Finished. Final Video File search in:- https://drive.google.com/drive/folders/1srcPN3mPRDpIe6f0V8Uw0AvHm4o5iTeH?usp=sharing")
divider()

empty_folder(TEMPORARY_PATH)

	
