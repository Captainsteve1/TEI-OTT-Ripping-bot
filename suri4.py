#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import os
import sys
import time
import urllib.parse
import requests
import random
import argparse 
import subprocess       
                                
import httpx
import typer
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from loguru import logger

from pywidevine.cdm import cdm, deviceconfig
from base64 import b64encode
from pywidevine.getPSSH import get_pssh
from pywidevine.decrypt.wvdecryptcustom import WvDecrypt
import config



class SunNXT(object):
    arguments = argparse.ArgumentParser()
    arguments.add_argument("-id", "--id", dest="media_id", help="content id ")
    arguments.add_argument("-q", "--quality", dest="res", help="quality of video")
    arguments.add_argument("-o", "--output", dest="output", help="output")
    args = arguments.parse_args()
    
    currentFile = __file__
    realPath = os.path.realpath(currentFile)
    dirPath = os.path.dirname(realPath)
    dirName = os.path.basename(dirPath)

    youtubedlexe = 'yt-dlp'
    aria2cexe = dirPath + '/bin/tools/aria2c'
    mp4decryptexe = dirPath + '/bin/tools/mp4decrypt'
    mkvmergeexe = dirPath + '/bin/tools/mkvmerge'
   
    def __init__(self):
        self.media_id = self.args.media_id
        self.audio_mpd = None
        self.video_mpd = None
        self.key = None
        self.mp4decryptexe =  self.dirPath + '/bin/tools/mp4decrypt'
        self.path = self.dirPath + "/output"

        if not os.path.exists(config.KEY_FILE):
            logger.error(
                f'{config.KEY_FILE} does not exist, run device_registration.py'
            )
            sys.exit()

        with open(config.KEY_FILE, 'r') as f:
            data = json.load(f)

        self.client_key = data['client_key']
        self.aes_secret = config.INIT_AES_SECRET[-4:] + \
                          data["device_id"][-8:].encode() + \
                          config.INIT_AES_SECRET[:4]
        proxies = {

    "https://": "https://SU2TuiBYWmMoNiNYPWuv2YXT:s799YY2jGXzHSWmWLJJQ5bye@in131.nordvpn.com:89",
        }
        self.session = requests.Session()
        self.session.headers.update(
            {
                'user-agent': config.UA,
                'clientKey': self.client_key,
                'X-myplex-platform': 'AndroidTV',
                'ContentLanguage': 'telugu',
                'Accept-Language': 'en'
            }
        )

    @staticmethod
    def encrypt(data: dict) -> str:
        cipher = AES.new(config.INIT_AES_SECRET, AES.MODE_CBC, iv=bytes([0] * 16))
        encrypted = cipher.encrypt(
            Padding.pad(json.dumps(data, separators=(',', ':')).encode(), 16)
        )
        return base64.b64encode(encrypted).decode()

    @staticmethod
    def decrypt(data: str, secret_key: bytes):
        cipher = AES.new(
            secret_key,
            AES.MODE_CBC,
            iv=bytes([0] * 16)
        )
        return json.loads(
            Padding.unpad(cipher.decrypt(base64.b64decode(data)), 16).decode()
        )
    def WV_Function(self,pssh, lic_url, cert_b64=None):
            headers = {
                'user-agent': config.UA,
                'clientKey': self.client_key,
                'X-myplex-platform': 'AndroidTV',
                'ContentLanguage': 'telugu',
                'Accept-Language': 'en'
            }
            proxy = {

    'https':'https://SU2TuiBYWmMoNiNYPWuv2YXT:s799YY2jGXzHSWmWLJJQ5bye@in131.nordvpn.com:89'

            }
            wvdecrypt = WvDecrypt(init_data_b64=pssh, cert_data_b64=cert_b64, device=deviceconfig.device_lenovolvl1)                   
            widevine_license = requests.post(url=lic_url, data=wvdecrypt.get_challenge(), headers=headers,proxies=proxy)
            license_b64 = b64encode(widevine_license.content)
            wvdecrypt.update_license(license_b64)
            Correct, keyswvdecrypt = wvdecrypt.start_process()
            if Correct:
             return Correct, keyswvdecrypt 
             
    def get_mpd_urls(self) -> tuple:
        proxy = {

    'https':'https://SU2TuiBYWmMoNiNYPWuv2YXT:s799YY2jGXzHSWmWLJJQ5bye@in131.nordvpn.com:89'
        }
        resp = self.session.get(config.MEDIA_URL.format(self.media_id),proxies=proxy)
       # print(resp.url)
      #  print(resp.json())
        data = self.decrypt(resp.json()['response'], self.aes_secret)
      #  print(data)

        subs = []
        for sub in data['results'][0]['subtitles']['values']:
            subs.append(
                {
                    'name': sub['language'],
                    'url': f"{sub['link_sub']}.vtt",
                    'lang': ''
                }
            )
        
        with open(config.SUBS_FILE, 'w') as f:
            f.write(json.dumps(subs))

        audio_mpd, video_mpd = None, None
        for video in data['results'][0]['videos']['values']:
            # download will give a flat file url for audio with ec3, but no 1080p
            # video
            if not audio_mpd and video['type'] == 'download' and video[
                    'profile'] == 'High':
                self.audio_mpd = video['link']

            if not video_mpd and video['profile'] == 'High' and video[
                    'type'] == 'streaming':
                self.video_mpd = video['link']
                
            if not video_mpd and video['profile'] == '4k_atmos' and video[
                    'type'] == 'streaming':
                self.atmos_4k_mpd = video['link']
                
        print('AUDIO MPD: ',self.audio_mpd)
        print('VIDEO MPD: ',self.video_mpd)
        print('4K MPD: ',self.atmos_4k_mpd) 
        video_pssh = get_pssh(self.video_mpd)
        audio_pssh = get_pssh(self.audio_mpd)
        print('PSSH: ',video_pssh)
        query = {
            'content_id': self.media_id,
            'licenseType': 'streaming',
            'timestamp': int(time.time()),
            'clientKey': self.client_key
        }
        print('LICENSE URL: ',f'{config.LICENSE_URL}?{urllib.parse.urlencode(query)}')
        lic_url = f'{config.LICENSE_URL}?{urllib.parse.urlencode(query)}'
        correct, video_keys = self.WV_Function(video_pssh, lic_url)
        correct, audio_keys = self.WV_Function(audio_pssh, lic_url)
        print('GETTING KEYS...')
        #for key in audi_keys:
         #  print('--key ' + key)
        
        v_key_list = []
        v_key_list.append(video_keys)

        count = 0
        for v_key in v_key_list:
          count = 1
          
        a_key_list = []
        a_key_list.append(audio_keys)

        count = 0
        for a_key in a_key_list:
          count = 1
       
        print("DONE..")
        print(v_key)
        print(a_key)
        #print(a_key)
        self.video_key = v_key[0]
        self.audio_key = v_key[2]
       # print(self.video_key)
        print("SELECTED Video KEY: ",self.video_key)
        print("SELECTED AUDIO KEY: " ,self.audio_key)
        return self.video_mpd,self.audio_mpd,video_pssh,audio_pssh,video_keys,lic_url,audio_keys
    
    def download(self):
        vide_mpd_url = self.video_mpd
        audio_mpd_url = self.audio_mpd
        video_key = self.video_key
        audio_key = self.audio_key
        mp4decrypt = self.mp4decryptexe
        output = self.args.output
        PATH = self.path
        if self.args.res == '480':
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', 'wa', '--fixup', 'never', audio_mpd_url,'-P',PATH, '-o', 'encrypted.m4a','--external-downloader-args', '-x 16 -s 16 -k 1M'])
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', 'bv*[height=480]', '--fixup', 'never', vide_mpd_url, '-P',PATH, '-o', 'encrypted.mp4','--external-downloader-args', '-x 16 -s 16 -k 1M'])    
           
        elif self.args.res == '720':
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', '1', '--fixup', 'never', audio_mpd_url, '-P',PATH,'-o', 'encrypted.m4a','--external-downloader-args', '-x 16 -s 16 -k 1M'])
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', 'bv*[height=720]', '--fixup', 'never', vide_mpd_url,'-P',PATH,  '-o', 'encrypted.mp4','--external-downloader-args', '-x 16 -s 16 -k 1M'])    
            
        elif self.args.res == '360':
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', '2', '--fixup', 'never', audio_mpd_url,'-P',PATH,  '-o', 'encrypted.m4a','--external-downloader-args', '-x 16 -s 16 -k 1M'])
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', 'bv*[height=360]', '--fixup', 'never', vide_mpd_url,'-P',PATH, '-o', 'encrypted.mp4','--external-downloader-args', '-x 16 -s 16 -k 1M'])    
           
        else:
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', '1', '--fixup', 'never', audio_mpd_url, '-P',PATH,'-o', 'encrypted.m4a','--external-downloader-args', '-x 16 -s 16 -k 1M --log "" --log-level error'])
            subprocess.run(['yt-dlp', '-k', '--allow-unplayable-formats', '--no-check-certificate', '-f', 'bv*[height=1080]', '--fixup', 'never', vide_mpd_url, '-P',PATH, '-o', 'encrypted.mp4','--external-downloader-args', '-x 16 -s 16 -k 1M --log "" --log-level error'])
            
        print("\nDecrypt chesthuna Uchaa Apukoo .....")
        subprocess.run([mp4decrypt,'--key',audio_key,PATH + '/' + 'encrypted.m4a',PATH +'/' + 'decrypted.m4a'])
        subprocess.run([mp4decrypt ,'--key', video_key,PATH + '/' + 'encrypted.mp4', PATH + '/' + 'decrypted.mp4'])  

        print('\nDONE..')
        
        print('\nMuxing....') 
        subprocess.run([self.mkvmergeexe,'--output',PATH + '/' + output +'.mkv', '--language', '0:eng',"--track-name","0:Trooporiginals", '--default-track', '0:yes', '--compression', '0:none', PATH +'/' + 'decrypted.mp4', '--language', '0:eng',"--track-name","1:Trooporiginals", '--default-track', '0:yes', '--compression' ,'0:none', PATH +'/' + 'decrypted.m4a','--language', '0:eng',"--track-name","0:Trooporiginals", '--default-track', '0:yes', '--compression', '0:none', PATH +'/' + 'decrypted.m4a', '--language', '0:eng',"--track-name","2:Trooporiginals",'--track-order', '0:0,1:0,2:0,3:0,4:0'])
        print("\nAll Done .....") 
  
        print("Cleaning Directory...")
        os.remove(PATH + '/'+ "encrypted.m4a")
        os.remove(PATH + '/' + "encrypted.mp4")
        os.remove(PATH + '/' + "decrypted.m4a")
        os.remove(PATH + '/' + "decrypted.mp4")   
        print("Uploading Gdrive..[Rclone] i love you ")
        subprocess.run(['rclone','copy', '/usr/src/app/output','Rose:'])
        print(" search here:- https://drive.google.com/drive/folders/1H0CZ5ddQkYAneXHecChziUsHMuTIt8Vg?usp=sharing") 
    '''def rclone(self):
       print("Uploading Gdrive..[Rclone]")
       output = self.path
       subprocess.run(['rclone','copy', output,'Rose:/'])
       print('Uploaded To Gdrive..')
       print('Search Your File in Here :- /list filename kottu ra ungga')
       '''
  
'''
    def parse_mpd(self, audio_mpd, video_mpd) -> tuple:
        audio_mpd_data = self.session.get(audio_mpd).content
        audio, _, subs, _ = utils.parse(audio_mpd, None, audio_mpd_data, presets=[])
        video_mpd_data = self.session.get(video_mpd).content
        _, video, _, pssh = utils.parse(video_mpd, None, video_mpd_data, config.PRESETS)
        return audio, video, pssh
        '''
'''
    def run(self):
        audio_mpd, video_mpd = self.get_mpd_urls()
        audio, video, pssh = self.parse_mpd(audio_mpd, video_mpd)
        print(f'{config.LICENSE_URL}?{urllib.parse.urlencode(query)}')
        query = {
            'content_id': self.media_id,
            'licenseType': 'streaming',
            'timestamp': int(time.time()),
            'clientKey': self.client_key
        }
        wv_keys = utils.get_wv_keys(
            f'{config.LICENSE_URL}?{urllib.parse.urlencode(query)}',
            pssh,
            config.CDM_DEVICE
        )
        logger.info(wv_keys)
'''

    #def download(self):
   
"""   
# ex. 117166
def main(media_id: str):
    s = SunNXT(media_id)
    s.run()
if __name__ == '__main__':
    typer.run(main)
 
"""

s = SunNXT()
s.get_mpd_urls()
s.download()
#s.rclone()
'''
sun = SunNXT()
#sun.encrypt(data)
#sun.decrypt()
sun.get_mpd_urls()
sun.WV_Function()
'''
