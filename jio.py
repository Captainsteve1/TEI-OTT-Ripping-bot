import requests, json
import os, sys
import argparse
import subprocess
import pathlib
import shutil

FILE_DIRECTORY=str(pathlib.Path(__file__).parent.absolute())
TEMPORARY_PATH = FILE_DIRECTORY+"/cache"
OUTPUT_PATH = FILE_DIRECTORY+"/output"
ENCODES = FILE_DIRECTORY+"/encodes"


# define paths
currentFile = __file__
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
dirName = os.path.basename(dirPath)
ytdl_path = "yt-dlp"
filedir=str(pathlib.Path(__file__).parent.absolute())
outputpath = filedir+"/output"
aria_path = aria_path = FILE_DIRECTORY+"/aria2cl"
# define 
def load_config():
    global ssotoken, uniqueID
    with open ("creds.txt", "r") as f:
        try:
            Creds = json.load(f)
            ssotoken = Creds['ssotoken']
            uniqueID = Creds['uniqueID']
        except json.JSONDecodeError:
            ssotoken = ''
            uniqueID = ''    

Request_URL = "https://prod.media.jio.com/apis/common/v3/playbackrights/get/"
Meta_URL = "https://prod.media.jio.com/apis/common/v3/metamore/get/"
#cachePath = 
#outPath = 
OTPSendURL = "https://prod.media.jio.com/apis/common/v3/login/sendotp"
OTPVerifyURL = "https://prod.media.jio.com/apis/common/v3/login/verifyotp"

def login(mobile_number):
    send = requests.post(url = OTPSendURL, headers = {
    'authority': 'prod.media.jio.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'origin': 'https://www.jiocinema.com',
    'referer': 'https://www.jiocinema.com/',
    },
     data = '{"number":"+91' + mobile_number +'"}'
    )
    if 'success' in str(send.content):
        OTP = input ('Enter OTP Received: ')
        verify = requests.post(url = OTPVerifyURL, headers = {
        'authority': 'prod.media.jio.com',
        'pragma': 'no-cache',
        'origin': 'https://www.jiocinema.com',
        'referer': 'https://www.jiocinema.com/',
        'deviceid': '1727391720'
        },
        data = '{"number":"+91' + mobile_number + '","otp":"' + OTP + '"}')
        creds = json.loads(verify.content)
        print (creds)
        load_creds(creds)
    else:
        print ("Wrong/Unregistered Mobile Number (ensure there's no +91 or 0 in the beginning)")
        sys.exit()

def load_creds(creds):
    try:
        ssotoken = creds['ssoToken']
        uniqueID = creds['uniqueId']
    except KeyError:
        print ("Wrong OTP, Try again!")
        sys.exit()
    Creds = {
        "ssotoken" : ssotoken,
        "uniqueID" : uniqueID
    }
    with open("creds.txt", "w") as f:
        f.write(json.dumps(Creds))

def get_manifest(VideoID):
    headers = {
    'authority': 'prod.media.jio.com',
    'pragma': 'no-cache',
    'ssotoken': ssotoken,
    'bitrates': 'true',
    'os': 'Android',
    'user-agent': 'JioOnDemand/1.5.2.1 (Linux;Android 4.4.2) Jio',
    'content-type': 'application/json',
    'accept': 'application/json, text/plain, */*',
    'devicetype': 'tv',
    }
    response = requests.post(url = Request_URL + VideoID , data = '{"uniqueId":"' + uniqueID + '"}' , headers = headers)
    return json.loads(response.text)

def get_m3u8(manifest):
    m3u8 = manifest['m3u8']['high']
    return m3u8

def divider():
	print ('-' * shutil.get_terminal_size().columns)

def mod_m3u8(url):
    mod = url.replace("jiovod.cdn.jio.com", "jiobeats.cdn.jio.com")
    lst = mod.split("/")
    lst[-1] = "chunklist.m3u8"
    mod = "/".join(lst)
    return mod

def get_metadata(VideoID):
    response = requests.get (url= Meta_URL + VideoID)
    return json.loads(response.text)

load_config()
if ssotoken == "" and uniqueID == "":
    M_No = input ('Enter Mobile Number: ')
    login (M_No)
    load_config()
arguments = argparse.ArgumentParser()
arguments.add_argument("-id", "--id", dest="id", help="content id ")
arguments.add_argument("-q", "--quality", dest="res", help="quality") 
args = arguments.parse_args()
VideoID = args.id
Troop = args.res
manifest = get_manifest(VideoID)
metadata = get_metadata(VideoID)
try:
    content_name = metadata['name']
except KeyError:
    print ("Incorrect/Malformed VideoID")
    sys.exit()
print (f'Downloading: {content_name} | {metadata["year"]} | {metadata["language"]}')
# print (f'Subtitles available: {metadata["subtitle"]}')    
fileName = f'{content_name}.{metadata["year"]}.{metadata["language"]}.AAC.x264.{Troop}.mp4'

def get_streams(m3u8):
    output = OUTPUT_PATH + '/' + f"{fileName}"
    print(f'link: {m3u8}') 
    print ("Shakthi Hero Ikkada")
    os.system('yt-dlp --external-downloader {aria_path} --no-warnings --allow-unplayable-formats --no-check-certificate -F "%s"'%m3u8)
    divider()
    VIDEO_ID = input("ENTER VIDEO_ID (Press Enter for Best): ")
    if VIDEO_ID == "":
           AUDIO_ID = "ba"
    divider()
    os.system(f'yt-dlp --no-warning --allow-unplayable-formats --user-agent "JioOnDemand/1.5.2.1 (Linux;Android 4.4.2)" -f {VIDEO_ID} --external-downloader-args "-x 16 -s 16 -k 1M" -o output "{m3u8}"')
    #os.rename(f'chunklist [chunklist].mp4', output)
    #print ("\nSuccessfully downloaded the stream!") 

def trackname():
        outputpath = OUTPUT_PATH + '/' + f"'{fileName}'"
        encodespath = ENCODES + '/' + f"'{fileName}'"
        divider()
        os.system('ffmpeg -i %s -hide_banner -map 0:v -map 0:a -map 0:s? -metadata title="TroopOriginals" -metadata:s:v title="TroopOriginals" -metadata:s:a title="TroopOriginals" -metadata:s:s title="TroopOriginals" -codec copy %s/thelidhu.mp4 && mv %s/thelidhu.mp4 %s'%(outputpath,OUTPUT_PATH,OUTPUT_PATH,encodespath))


def rclone():
    print("Aagu Ra Nakka Pumka")
    encodespath =  ENCODES + '/' + f"{fileName}"
    subprocess.run(['rclone','move', encodespath,'Rose:/jio'])
    print("SHAKTHI HERO THELUSA THAMMUDU NEEKU https://drive.google.com/drive/folders/1HGFtdd5xZ4Obo11HCaphApRmqmFTbp4A?usp=sharing") 


m3u8_url = get_m3u8(manifest)
nonDRM_m3u8_url = mod_m3u8(m3u8_url)
get_streams(nonDRM_m3u8_url)
divider()
trackname()
rclone()
