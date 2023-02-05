import json
import shutil
import xml
import ffmpy
import requests
import rich_argparse
from colorama import Fore, Back, Style
from colorama import just_fix_windows_console
from argparse import RawDescriptionHelpFormatter
import base64
import jwt
import os
import subprocess
import time
import psutil
import sys
import xmltodict
import binascii
from rich_argparse import RawTextRichHelpFormatter
from pywidevine.cdm import cdm, deviceconfig
from base64 import b64encode
from pywidevine.getPSSH import get_pssh
from pywidevine.decrypt.wvdecryptcustom import WvDecrypt
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("Aha Ripper by SAiTAMA")
import argparse
import glob
import re
import prettytable

tablee = prettytable.PrettyTable()
from progress.bar import IncrementalBar

just_fix_windows_console()

main_dir = os.getcwd()

mode = 'AHA'

n_m3u8dl_reexe = f'{main_dir}\\binaries\\N_m3u8DL-RE.exe'
mp4dumpexe = f'{main_dir}\\binaries\\mp4dump.exe'
mp4decryptexe = f'{main_dir}\\binaries\\mp4decrypt.exe'
mkvmergeexe = f'{main_dir}\\binaries\\mkvmerge.exe'
mediainfoexe = f'{main_dir}\\binaries\\MediaInfo.exe'
ffmpeg_path = f'{main_dir}\\binaries\\ffmpeg.exe'
n_m3u8dl_re_arguments = ' --save-dir temp --save-name input --tmp-dir temp --log-level ERROR --binary-merge True -mt True '

dirs = ['downloads', 'temp']

for dire in dirs:
    if os.path.exists(f'{main_dir}/{dire}'):
        pass
    else:
        os.makedirs(f'{main_dir}/{dire}')


def args_parser():
    parser = argparse.ArgumentParser(
        formatter_class=RawTextRichHelpFormatter,
        description="Aha Ripper By SAiTAMA")
    parser.add_argument(
        '-keys',
        '--keys-only',
        dest='keys',
        action='store_true',
        help="Print Keys Only and Exit"
    )
    parser.add_argument(
        '--subs-only',
        dest='subs_only',
        action='store_true',
        help='Download Only Subs and Skip Downloading Video and Audio'
    )
    parser.add_argument(
        '--no-audio',
        dest='no_audio',
        action='store_true',
        help="Don't Download Audio and Download Both subtitles and Video"
    )
    parser.add_argument(
        '--no-video',
        dest='no_video',
        action='store_true',
        help='Don\'t Download Video and Download Both Audio and Subtitles'
    )
    parser.add_argument(
        "--url",
        "-u",
        help="URL of any Movie or Episode (can download whole series)"
    )
    parser.add_argument(
        '-qa',
        dest='audio_quality',
        help='Audio Quality to Download'
    )
    parser.add_argument(
        "-q",
        "--quality",
        help="Video Resolution: 144, 240, 360, 480, 540, 720, 1080, 2160"
    )
    parser.add_argument(
        '-gn',
        '--group-name',
        default='',
        dest='GROUP',
        help='Your Group Name'
    )
    parser.add_argument(
        '-ss',
        '--season-start',
        help='Specify Season Start'
    )
    parser.add_argument(
        '-se',
        '--season-end',
        help='Specify Season End\n(Note: This cannot be Zero)'
    )
    parser.add_argument(
        '-es',
        '--episode-start',
        help='Specify Episode Start in a Season\n(Note: This cannot be Zero)'
    )
    parser.add_argument(
        '-ee',
        '--episode-end',
        help='Specify Episode End in a Season\n(Note: This cannot be Zero)'
    )

    args = parser.parse_args()

    if args.season_start == '0' or args.season_end == '0':
        print(Fore.RED + '\nSeason Start or Season End Cannot Be Zero' + Fore.RESET)
        exit()
    if args.episode_start == '0' or args.episode_end == '0':
        print(Fore.RED + '\nEpisode Start or Episode End cannot be Zero')
        exit()

    return args


arguments = args_parser()
# print(arguments)
# exit()
if not arguments.quality:
    quality = ''
else:
    quality = int(arguments.quality)
    if quality == 2160:
        dl_quality = 3840
    elif quality == 1080:
        dl_quality = 1920
    elif quality == 720:
        dl_quality = 1280
    elif quality == 720:
        dl_quality = 1280
    elif quality == 540:
        dl_quality = 960
    elif quality == 480:
        dl_quality = 864
    elif quality == 360:
        dl_quality = 640
    elif quality == 240:
        dl_quality = 480
    elif quality == 144:
        dl_quality = 320
    else:
        dl_quality = 320


def kill_processes(pid):
    '''Kills parent and children processess'''
    parent = psutil.Process(pid)
    # kill all the child processes
    for child in parent.children(recursive=True):
        child.kill()
    # kill the parent process
    parent.kill()


def get_auths():
    headers = {
        'authority': 'auth-platform.api.aha.firstlight.ai',
        'accept': '*/*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    data = {
        'client_id': 'android-ui-app',
        'client_secret': 'fd14a6bc-2389-41c2-9543-044224a402d2',
        'grant_type': 'client_credentials',
        'audience': 'edge-service',
        'scope': 'offline openid',
    }

    response = requests.post('https://auth-platform.api.aha.firstlight.ai/oauth2/token', headers=headers, data=data)

    authorization = "Bearer " + response.json()['access_token']

    with open("aha token.txt") as refreshToken:
        refreshToken = refreshToken.read()

    headers = {
        'authority': 'rest-prod-aha.evergent.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    json_data = {
        'RefreshTokenRequestMessage': {
            'refreshToken': f'{refreshToken}',
            'channelPartnerID': 'ARHAMEDIA',
            'apiUser': 'ahaapiuser',
            'apiPassword': 'Aha@p!u$#r123#$',
        },
    }

    response = requests.post('https://rest-prod-aha.evergent.com/aha/refreshToken', headers=headers, json=json_data)

    x_auth = "Bearer " + response.json()['RefreshTokenResponseMessage']['accessToken']

    headers = {
        'authority': 'rest-prod-aha.evergent.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'authorization': f'{x_auth}',
        'content-type': 'application/json',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    json_data = {
        'GetEntitlementsRequestMessage': {
            'contactID': '339190916',
            'channelPartnerID': 'AHA_IN',
            'apiUser': 'ahaapiuser',
            'apiPassword': 'Aha@p!u$#r123#$',
            'returnUpgradableFlag': 'true',
            'returnProductAttributes': 'true',
        },
    }

    response = requests.post('https://rest-prod-aha.evergent.com/aha/getEntitlements', headers=headers, json=json_data)

    x_authorization = response.json()['GetEntitlementsResponseMessage']['ovatToken']

    with open("device_id.txt") as dev_id:
        deviceID = dev_id.read()

    headers = {
        'authority': 'device-register-service.api.aha.firstlight.ai',
        'authorization': authorization,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        'x-client-id': 'firstlight-main-iosmobile',
        'x-authorization': x_authorization,
    }

    response = requests.post(url='https://device-register-service.api.aha.firstlight.ai/device/app/register',
                             headers=headers, data='{"uniqueId":"' + deviceID + '"}')

    secret = json.loads(response.content)['data']['secret']
    servertime = int(json.loads(response.content)['header']['system_time'])

    jwttime = (servertime) / 1000

    x_device_id = jwt.encode({
        "deviceId": deviceID,
        "aud": "playback-auth-service",
        "iat": jwttime,
        "exp": jwttime + 30
    }, base64.b64decode(secret), algorithm="HS256")

    return authorization, x_auth, x_device_id, deviceID, x_authorization


def getSeasonContentIDs(url):
    whole_series_id, acl = getEpisodesInfo(url)

    headers = {
        'authority': 'data-store-cdn.api.aha.firstlight.ai',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    params = {
        'pageNumber': '1',
        'pageSize': '50',
        'reg': 'in',
        'acl': f'{acl}',
        'dt': 'web',
    }

    response = requests.get(
        f'https://data-store-cdn.api.aha.firstlight.ai/content/webseries/{whole_series_id}/webseasons',
        params=params,
        headers=headers,
    )

    sea_nums = []
    season_ids = []

    num = len(response.json()['data'])

    for n in range(len(response.json()['data'])):
        ex_id_list = response.json()['data'][n]['ex_id'].split('-')
        if f's{num}' in ex_id_list or f'S{num}' in ex_id_list or f's0{num}' in ex_id_list or f'S0{num}' in ex_id_list:
            sea_num = f's{num}'.split('s')[-1]
            season_id = response.json()['data'][n]['id']
            season_ids.append(season_id)
            num = num - 1
            sea_nums.append(sea_num)
    sea_nums.sort()
    season_ids = season_ids[::-1]
    return season_ids, sea_nums


def getEpisodesInfo(url):
    season_link_list = url.split('-')
    episode_name = url.split('/')[-1]

    # Getting Season Number
    for n in range(len(season_link_list)):
        if f's{n}' in season_link_list:
            sea_num = f's{n}'.split('s')[-1]
            season_in_link = f'S{sea_num}'
    # Getting Season

    headers = {
        'authority': 'data-store-cdn.api.aha.firstlight.ai',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    params = {
        'reg': 'in',
        'acl': 'te',
        'dt': 'web',
    }

    response = requests.get(
        f'https://data-store-cdn.api.aha.firstlight.ai/content/urn/resource/catalog/webepisode/{episode_name}',
        params=params,
        headers=headers,
    )

    whole_series_id = response.json()['data']['stl_id']

    acl = response.json()['data']['acl']

    return whole_series_id, acl


def getEpisodes(url):
    url = url.split('/')[-1]

    whole_series_id, acl = getEpisodesInfo(url)

    season_ids, sea_nums = getSeasonContentIDs(url)

    names = []
    episode_names = []
    contentIDs = []
    years = []
    acls = []
    is_4k = []
    audio_qualities = []

    print(Fore.LIGHTBLACK_EX + '\nNo. of Available Seasons: ' + str(len(season_ids)) + Fore.RESET)

    if arguments.season_start is None and arguments.season_end is None:
        season_range = input('\nEnter Season Range (Ex: 1-1 (or) 1-2): ')
        season_range = season_range.split('-')
        season_start = int(season_range[0])
        season_end = int(season_range[1])
    elif arguments.season_start is not None and arguments.season_end is not None:
        season_start = int(arguments.season_start)
        season_end = int(arguments.season_end)
    elif arguments.season_start is not None and arguments.season_end is None:
        season_start = int(arguments.season_start)
        season_end = len(season_ids)
    else:
        season_start = 1
        season_end = len(season_ids)

    if int(season_end) > len(season_ids):
        print(Fore.RED + f'\nThe No. of Seasons is {len(season_ids)} and you entered {season_end} at Season End\nExiting Now . . . ' + Fore.RESET)
        exit()
    if int(season_start) > len(season_ids):
        print(Fore.RED + f'\nThe No. of Seasons is {len(season_ids)} and you entered {season_end} at Season Start\nExiting Now . . . ' + Fore.RESET)
        exit()

    headers = {
        'authority': 'data-store-cdn.api.aha.firstlight.ai',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    for num_seas in range(season_start - 1, season_end):

        params = {
            'seasonId': f'{season_ids[num_seas]}',
            'pageNumber': '1',
            'pageSize': '100',
            'reg': 'in',
            'acl': f'{acl}',
            'dt': 'web',
        }

        response = requests.get(
            f'https://data-store-cdn.api.aha.firstlight.ai/content/webseries/{whole_series_id}/webepisodes',
            params=params,
            headers=headers
        )
        with open('sin.json', mode='w') as f:
            json.dump(response.json(), f, indent=4)
        episode_num = 1

        for i in range(len(response.json()['data'])):
            content_id = response.json()['data'][i]['id']
            acl = response.json()['data'][i]['acl']
            is_4k_episode = response.json()['data'][i]['vq']
            aq = response.json()['data'][i]['aq']
            audio_qualities.append(aq)
            acls.append(acl)
            contentIDs.append(content_id)
            is_4k.append(is_4k_episode)
            year = str(response.json()['data'][i]['r'])
            years.append(year)
            for n in range(len(response.json()['data'][i]['losetl'])):
                if response.json()['data'][i]['losetl'][n]['lang'] == 'en':
                    name = response.json()['data'][i]['losetl'][n]['n']
                    if 'Season' in name:
                        name = name.split('Season')[0].strip()
                        season_name = name
                    if response.json()['data'][i]['lon'][1]['lang'] == 'en':
                        episode_name = response.json()['data'][i]['lon'][1]['n']
                    else:
                        episode_name = response.json()['data'][i]['lon'][0]['n']
                    name = name.replace(f' S{n}', '').replace(f' s{n}', '').replace(f' E{n}', '').replace(f' e{n}',
                                                                                                          '').replace(
                        f' S0{n}', '').replace(f' s0{n}', '').replace(f' E0{n}', '').replace(f' e0{n}', '')
                    if name in episode_name:
                        episode_name = episode_name.split(name)[-1].strip()
                    episode_name = episode_name.replace(f'Episode {episode_num}', f'E{episode_num}').replace(
                        f'episode {episode_num}', f'E{episode_num}')
                    episode_name = episode_name.replace('Season', 'S').replace('season', 'S').replace(f'{episode_num} ',
                                                                                                      '').replace(
                        f' {num_seas + 1} ', '').replace(f'{num_seas + 1} ', '')
                    if year in name:
                        name = name.replace(year, f'({year})') + f' S{num_seas + 1} ' + episode_name
                    else:
                        name = name + f' ({year}) ' + f' S{num_seas + 1} ' + episode_name
                    if f'E{episode_num}' not in name:
                        name = name.replace(f'S{num_seas + 1}', f'S{num_seas + 1} E{episode_num}')
                    name = name.replace('   ', ' ').replace('  ', ' ').replace(f' Episode {episode_num}', '').replace(
                        f' episode {episode_num}', '').replace(f' Episode {episode_num - 1}', '').replace(
                        f' episode {episode_num - 1}', '').replace(f' Episode {episode_num - 2}', '').replace(
                        f' episode {episode_num - 2}', '').replace(f' Episode {episode_num - 3}', '').replace(
                        f' episode {episode_num - 3}', '')
                    name = name.replace(f'Episode {episode_num}', f'E{episode_num}').replace(
                        f'Episode {episode_num - 1}', '').replace(' S 01', '').replace(' S 02', '').replace(' S 03',
                                                                                                            '').replace(
                        ' S 04', '').replace(' S 05', '').replace(' Season 1', '').replace(' season 1', '').replace(
                        ' Season 2', '').replace(' season 2', '').replace(' Season 3', '').replace(' season 3',
                                                                                                   '').replace(
                        ' Season 4', '').replace(' season 4', '').title()
                    names.append(name)
                    episode_names.append(episode_name)
                    episode_num += 1

        # print(episode_names)
        # print(names)
    # print(episode_names)
    # print(names)
    print(Fore.LIGHTBLACK_EX + '\nNo. of Avaialble Episodes: ' + str(len(contentIDs)) + Fore.RESET)

    return episode_names, names, contentIDs, acls, is_4k, audio_qualities


def getMovieDetails(url):
    url = url.split('/')[-1]

    headers = {
        'authority': 'data-store-cdn.api.aha.firstlight.ai',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }

    params = {
        'reg': 'in',
        'acl': 'te',
        'dt': 'web',
    }

    response = requests.get(
        f'https://data-store-cdn.api.aha.firstlight.ai/content/urn/resource/catalog/movie/{url}',
        params=params,
        headers=headers,
    )

    acl = response.json()['data']['acl']
    contentID = response.json()['data']['id']

    for n in range(len(response.json()['data']['lon'])):
        if response.json()['data']['lon'][n]['lang'] == 'en':
            name = response.json()['data']['lon'][n]['n']
    is_4k_movie = response.json()['data']['vq']
    year = str(response.json()['data']['r'])

    # print(name, year, acl, contentID)

    return acl, contentID, year, name, is_4k_movie


def getMPDs(url):

    global authorization, x_auth, x_device_id, deviceID, x_authorization, dl_quality

    headers = {
        'authority': 'playback-auth-service.api.aha.firstlight.ai',
        'accept': '*/*',
        'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
        'authorization': f'{authorization}',
        'content-type': 'application/json',
        'origin': 'https://www.aha.video',
        'referer': 'https://www.aha.video/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-authorization': f'{x_authorization}',
        'x-client-id': 'firstlight-main-iosmobile',
        'x-device-id': f'{x_device_id}',
    }

    if catalogType == 'webepisode':

        episode_names, names, contentIDs, acls, is_4k, audio_qualities = getEpisodes(url)

        episodes_quality = []

        for k_num in range(len(is_4k)):
            if is_4k[k_num] == '4K':
                episodes_quality.append(str(k_num + 1))

        # print(Fore.LIGHTBLACK_EX + f'\nNo. of 4K episodes available: {len(episodes_quality)}' + Fore.RESET)

        if len(episodes_quality) != 0:
            if len(episodes_quality) == len(is_4k) or len(episodes_quality) == len(is_4k) - 1:
                print(Fore.LIGHTGREEN_EX + f'\nAll Episodes are available in 4K' + Fore.RESET)
                download_4k = True
            else:
                print(Fore.LIGHTGREEN_EX + f'\n4K episodes: ' + Fore.LIGHTGREEN_EX + f'{" ".join(episodes_quality)}' + Fore.RESET)
                print()
                download_4k = True
        else:
            print(Fore.LIGHTRED_EX + '\nNo 4K available' + Fore.RESET)
            download_4k = False

        if arguments.quality is not None:
            if not download_4k and int(arguments.quality) > 1080:
                print(Fore.RED + '\nDownloading 1080p . . .' + Fore.RESET)
                dl_quality = 1080

        if arguments.episode_start is None and arguments.episode_end is None:
            episode_range = input('\nEnter Episode Range (Ex: 2-6 (or) 8-8): ')
            episode_start = int(episode_range.split('-')[0])
            episode_end = int(episode_range.split('-')[1])
        elif arguments.episode_start is not None and arguments.episode_end is not None:
            episode_start = int(arguments.episode_start)
            episode_end = int(arguments.episode_end)
        elif arguments.episode_start is not None and arguments.episode_end is None:
            episode_start = int(arguments.episode_start)
            episode_end = int(input('\nEnter Episode End: '))
        else:
            episode_start = 1
            episode_end = len(contentIDs)

        if int(episode_end) > len(contentIDs):
            print(
                Fore.RED + f'The Total No. of Episodes is {len(contentIDs)} and you entered {episode_end} at Episode End\nExiting Now . . .' + Fore.RESET)
            exit()

        if int(episode_start) > len(contentIDs):
            print(
                Fore.RED + f'The Total No. of Episodes is {len(contentIDs)} and you entered {episode_start} at Episode Start\nExiting Now . . .' + Fore.RESET)
            exit()

        for n in range(episode_start - 1, episode_end):

            x_device_id = gen_x_device_id()

            headers = {
                'authority': 'playback-auth-service.api.aha.firstlight.ai',
                'accept': '*/*',
                'accept-language': 'en,en-US;q=0.9,en-GB;q=0.8',
                'authorization': f'{authorization}',
                'content-type': 'application/json',
                'origin': 'https://www.aha.video',
                'referer': 'https://www.aha.video/',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'sec-gpc': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                'x-authorization': f'{x_authorization}',
                'x-client-id': 'firstlight-main-iosmobile',
                'x-device-id': f'{x_device_id}',
            }

            json_data = {
                'deviceName': 'mobileweb',
                'deviceId': f'{deviceID}',
                'contentId': f'{contentIDs[n]}',
                'contentTypeId': 'vod',
                'catalogType': 'webepisode',
                'mediaFormat': 'dash',
                'drm': 'widevine',
                'delivery': 'streaming',
                'disableSsai': 'false',
                'deviceManufacturer': 'mobile-web',
                'deviceModelName': 'web',
                'deviceModelNumber': 'chrome',
                'deviceOs': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                'deviceToken': f'{x_device_id}',
            }

            try:
                response = requests.post(
                    'https://playback-auth-service.api.aha.firstlight.ai/media/content/authorize',
                    headers=headers,
                    json=json_data,
                )
                mpd = response.json()['data']['contentUrl'].split('?')[0]
                lic_url = response.json()['data']['licenseUrl']
            except requests.exceptions.ConnectionError:
                try:
                    response = requests.post(
                        'https://playback-auth-service.api.aha.firstlight.ai/media/content/authorize',
                        headers=headers,
                        json=json_data,
                    )
                    mpd = response.json()['data']['contentUrl'].split('?')[0]
                    lic_url = response.json()['data']['licenseUrl']
                except KeyError:
                    time.sleep(3)
                    response = requests.post(
                        'https://playback-auth-service.api.aha.firstlight.ai/media/content/authorize',
                        headers=headers,
                        json=json_data,
                    )
                    mpd = response.json()['data']['contentUrl'].split('?')[0]
                    lic_url = response.json()['data']['licenseUrl']
            except KeyError:
                # print('Error Getting MPD')
                try:
                    response = requests.post(
                        'https://playback-auth-service.api.aha.firstlight.ai/media/content/authorize',
                        headers=headers,
                        json=json_data,
                    )
                    mpd = response.json()['data']['contentUrl'].split('?')[0]
                    lic_url = response.json()['data']['licenseUrl']
                except KeyError:
                    time.sleep(3)
                    response = requests.post(
                        'https://playback-auth-service.api.aha.firstlight.ai/media/content/authorize',
                        headers=headers,
                        json=json_data,
                    )
                    mpd = response.json()['data']['contentUrl'].split('?')[0]
                    lic_url = response.json()['data']['licenseUrl']

            for s_n in range(5):
                if str(s_n) in names[n].split('(')[0]:
                    replaced_name = names[n].split('(')[0].split(' ')[-1]
                    if replaced_name == '' or replaced_name == ' ':
                        replaced_name = names[n].split('(')[0].split(' ')[-2].split(f'{s_n}')[0]
                    else:
                        replaced_name = names[n].split('(')[0].split(' ')[-1].split(f'{s_n}')[0]
                    names[n] = names[n].replace(f'{replaced_name}{s_n}', replaced_name)
            fix_season_name = names[n].split('(')[0]
            if fix_season_name in names[n].split(')')[-1]:
                names[n] = names[n].split(')')[0] + ')' + names[n].split(')')[-1].replace(f' {fix_season_name}', ' ')
            names[n] = names[n].replace('  ', '')
            mp4decrypt_keys, mpd_content = getKeys(mpd, lic_url=lic_url, name=names[n])

            if not arguments.keys:
                download_time_min_start = time.localtime().tm_min
                download_time_sec_start = time.localtime().tm_sec
                download_main(MPD_URL=mpd, MPD_resp=mpd_content, dl_name=names[n])
                download_time_min_end = time.localtime().tm_min
                download_time_sec_end = time.localtime().tm_sec
                time_took_to_download_in_min = int(download_time_min_end - download_time_min_start)
                if '-' in str(time_took_to_download_in_min):
                    time_took_to_download_in_min = int(60-(int(time_took_to_download_in_min))*-1)
                time_took_to_download_in_sec = int(download_time_sec_end - download_time_sec_start)
                if int(download_time_min_end - download_time_min_start) > 60:
                    print(
                        Fore.LIGHTRED_EX + f"Time taken to download: {round(time_took_to_download_in_min / 60, 2)} hours\nDude, it's time to upgrade your internet..." + Fore.RESET)
                elif time_took_to_download_in_min == 0:
                    print(
                        Fore.YELLOW + f"\nTime taken to download: {time_took_to_download_in_sec} seconds..." + Fore.RESET)
                elif '-' in str(time_took_to_download_in_sec):
                    if time_took_to_download_in_min - 1 == 0:
                        print(
                            Fore.YELLOW + f"\nTime taken to download: {60 - (time_took_to_download_in_sec * -1)} seconds..." + Fore.RESET)
                    elif time_took_to_download_in_min - 1 == 1:
                        print(
                            Fore.YELLOW + f"\nTime taken to download: {time_took_to_download_in_min - 1} minute and {60 - (time_took_to_download_in_sec * -1)} seconds..." + Fore.RESET)
                    else:
                        print(
                            Fore.YELLOW + f"\nTime taken to download: {time_took_to_download_in_min - 1} minutes and {60 - (time_took_to_download_in_sec * -1)} seconds..." + Fore.RESET)
                else:
                    print(
                        Fore.YELLOW + f"\nTime taken to download: {time_took_to_download_in_min} minutes and {time_took_to_download_in_sec} seconds..." + Fore.RESET)
                print()

                acl = acls[n]

                time_merge_start_min = time.localtime().tm_min
                time_merge_start_sec = time.localtime().tm_sec
                deceryptAndMerge(names[n], mp4decrypt_keys, language=acl)
                time_merge_end_min = time.localtime().tm_min
                time_merge_end_sec = time.localtime().tm_sec
                time_took_merge_min = int(time_merge_end_min - time_merge_start_min)
                time_took_merge_sec = int(time_merge_end_sec - time_merge_start_sec)
                if arguments.no_video:
                    pass
                elif arguments.no_audio:
                    pass
                elif arguments.subs_only:
                    pass
                else:
                    if time_took_merge_min == 0:
                        print(Fore.YELLOW + f"\nTime taken to mux: {time_took_merge_sec} seconds..." + Fore.RESET)
                    elif '-' in str(time_took_merge_sec) and time_took_merge_min == 0:
                        print(
                            Fore.YELLOW + f"\nTime taken to mux: {60 - (time_took_merge_sec * -1)} seconds..." + Fore.RESET)
                    elif '-' in str(time_took_merge_sec):
                        if time_took_merge_min - 1 == 0:
                            print(
                                Fore.YELLOW + f"\nTime taken to mux: {60 - (time_took_merge_sec * -1)} seconds..." + Fore.RESET)
                        elif time_took_merge_min - 1 == 1:
                            print(
                                Fore.YELLOW + f"\nTime taken to mux: {time_took_merge_min - 1} minute and {60 - (time_took_merge_sec * -1)} seconds..." + Fore.RESET)
                        else:
                            print(
                                Fore.YELLOW + f"\nTime taken to mux: {time_took_merge_min - 1} minutes and {60 - (time_took_merge_sec * -1)} seconds..." + Fore.RESET)
                    elif time_took_merge_min == 1:
                        print(
                            Fore.YELLOW + f"\nTime taken to mux: {time_took_merge_min} minute and {time_took_merge_sec} seconds..." + Fore.RESET)
                    else:
                        print(
                            Fore.YELLOW + f"\nTime taken to mux: {time_took_merge_min} minutes and {time_took_merge_sec} seconds..." + Fore.RESET)
                    print()

    else:

        acl, contentID, year, name, is_4k_movie = getMovieDetails(url)

        json_data = {
            'deviceName': 'mobileweb',
            'deviceId': f'{deviceID}',
            'contentId': f'{contentID}',
            'contentTypeId': 'vod',
            'catalogType': 'movie',
            'mediaFormat': 'dash',
            'drm': 'widevine',
            'delivery': 'streaming',
            'disableSsai': 'false',
            'deviceManufacturer': 'mobile-web',
            'deviceModelName': 'web',
            'deviceModelNumber': 'chrome',
            'deviceOs': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'deviceToken': f'{x_device_id}',
        }

        response = requests.post(
            'https://playback-auth-service.api.aha.firstlight.ai/media/content/authorize',
            headers=headers,
            json=json_data,
        )

        if is_4k_movie == '4K':
            print(Fore.LIGHTGREEN_EX + f'\n{name} ({year}) is available in 4K' + Fore.RESET)
        else:
            print(Fore.LIGHTYELLOW_EX + f'\nNo 4K available for {name} ({year})' + Fore.RESET)
        if acl.lower() == 'te':
            fixed_a_lang = 'Telugu'
        elif acl.lower() == 'ta':
            fixed_a_lang = 'Tamil'
        elif acl.lower() == 'kn':
            fixed_a_lang = 'Kannada'
        else:
            fixed_a_lang = 'English'

        if arguments.quality is not None:
            if is_4k_movie != '4K' and int(arguments.quality) > 1080:
                print(Fore.RED + '\nDownloading 1080p . . .' + Fore.RESET)
                dl_quality = 1920

        print(Fore.LIGHTMAGENTA_EX + f'\n[+] Language: ' + Fore.LIGHTBLUE_EX + f'{fixed_a_lang}' + Fore.RESET)
        mpd = response.json()['data']['contentUrl'].split('?')[0]
        lic_url = response.json()['data']['licenseUrl']
        mp4decrypt_keys, mpd_contents = getKeys(mpd, lic_url=lic_url, name=f'{name} ({year})')
        name = f'{name} ({year})'
        if not arguments.keys:
            download_main(MPD_URL=mpd, MPD_resp=mpd_contents, dl_name=name)
            deceryptAndMerge(name, mp4decrypt_keys, language=acl)


def getKeys(mpd, lic_url, name):

    try:
        with open(f'{main_dir}\\pywidevine\\Keys\\AHA Keys.json', mode='r') as keys_data_file:
            keys_data_read = json.load(keys_data_file)
        for num in range(len(keys_data_read)):
            if keys_data_read[num]['Title'] == name:
                s_append = False
                print(Fore.LIGHTGREEN_EX + '\nKeys Found in JSON' + Fore.RESET)
                break
            else:
                s_append = True
    except FileNotFoundError:
        pass
    subprocess.run(f'"{main_dir}\\binaries\\aria2c.exe" -o "temp\\input.mpd" --max-tries=0 "{mpd}"', stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    try:
        with open(f'{main_dir}\\temp\\input.mpd') as f:
            contents = f.read()
        os.remove(f'{main_dir}\\temp\\input.mpd')
        r = contents
        mpd_contents = json.loads(json.dumps(xmltodict.parse(r)))
    except xml.parsers.expat.ExpatError:
        print(Fore.RED + 'Error Getting MPD . . .' + Fore.RESET)
        exit()

    PSSH = mpd_contents['MPD']['Period']['AdaptationSet'][0]['ContentProtection']

    for num in range(len(PSSH)):
        if PSSH[num]['@schemeIdUri'] == 'urn:uuid:EDEF8BA9-79D6-4ACE-A3C8-27DCD51D21ED':
            PSSH = PSSH[num]['cenc:pssh']

    print(Fore.LIGHTBLUE_EX + '\n[+] Downloading: ' + Fore.LIGHTMAGENTA_EX + f'{name}' + Fore.RESET)

    # print(Fore.LIGHTBLUE_EX + f'\n[+] PSSH Found: ' + Fore.LIGHTBLACK_EX + f'{PSSH}' + Fore.RESET)

    def WV_Function(pssh, lic_url, cert_b64=None):
        headers = {
            'authority': 'playback-auth-service.api.aha.firstlight.ai',
            'accept': '*/*',
            'accept-language': 'en;q=0.7',
            'authorization': f'{authorization}',
            'origin': 'https://www.aha.video',
            'referer': 'https://www.aha.video/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'x-authorization': f'{x_authorization}',
            'x-client-id': 'firstlight-main-iosmobile',
            'x-device-id': f'{x_device_id}',
        }

        wvdecrypt = WvDecrypt(init_data_b64=pssh, cert_data_b64=cert_b64, device=deviceconfig.device_android_generic)
        widevine_license = requests.post(url=lic_url, data=wvdecrypt.get_challenge(), headers=headers)
        license_b64 = b64encode(widevine_license.content)
        wvdecrypt.update_license(license_b64)
        Correct, keyswvdecrypt = wvdecrypt.start_process()
        if Correct:
            return Correct, keyswvdecrypt

    try:
        correct, keys = WV_Function(PSSH, lic_url)
    except requests.exceptions.ConnectionError:
        correct, keys = WV_Function(PSSH, lic_url)
    mp4decrypt_keys = ''
    keys_data = ''
    for key in keys:
        keys_data = keys_data + key + '\n'
    keys_data = keys_data.strip()
    keys_data_json = {
        'Title': f'{name}',
        'MPD': f'{mpd}',
        'Keys': f'{keys_data}'
    }
    try:
        with open(f'{main_dir}\\pywidevine\\Keys\\AHA Keys.json', mode='r') as keys_data_file:
            keys_data_read = json.load(keys_data_file)
    except FileNotFoundError:
        keys_data_json = [
            {
                'Title': f'{name}',
                'MPD': f'{mpd}',
                'Keys': f'{keys_data}'
            }
        ]
        with open(f'{main_dir}\\pywidevine\\Keys\\AHA Keys.json', mode='w') as keys_data_file:
            json.dump(keys_data_json, keys_data_file, indent=4)
    else:
        if s_append:
            keys_data_read.append(keys_data_json)
            with open(f'{main_dir}\\pywidevine\\Keys\\AHA Keys.json', mode='w') as keys_data_file:
                json.dump(keys_data_read, keys_data_file, indent=4)
    print(Fore.YELLOW + "\n==============================KEYS===============================" + Fore.RESET)
    keys_data = ''
    for key in keys:
        mp4decrypt_keys = mp4decrypt_keys + f'--key {key} '
        print(Fore.LIGHTGREEN_EX + "\n" + key + Fore.RESET)
        keys_data = keys_data + key + '\n'

    print(Fore.YELLOW + '\n=================================================================' + Fore.RESET)
    return mp4decrypt_keys, r


def download_main(MPD_URL, MPD_resp, dl_name):
    MPD = MPD_URL
    r = MPD_resp
    contents = json.loads(json.dumps(xmltodict.parse(r)))

    media = contents['MPD']['Period']['AdaptationSet'][0]['SegmentTemplate']['@media']
    # time = contents['MPD']['Period']['AdaptationSet'][0]['SegmentTemplate']['SegmentTimeline']['S'][0]['@t']
    media = media.split('?')[0]
    adaptation = contents['MPD']['Period']['AdaptationSet']
    if not arguments.subs_only:
        for n in range(len(adaptation)):
            if '"384000"' and '"192000"' in r:
                if adaptation[n]['@contentType'] == 'audio' and adaptation[n]['@maxBandwidth'] == '384000':
                    representation = adaptation[n]['Representation']
                    codec = adaptation[n]['@codecs'].split('.')[0]
                    rep_num = n
                elif adaptation[n]['@contentType'] == 'audio':
                    ano_representation = adaptation[n]['Representation']
                    ano_codec = adaptation[n]['@codecs'].split('.')[0]
                    ano_rep_num = n
            elif adaptation[n]['@contentType'] == 'audio':
                representation = adaptation[n]['Representation']
                ano_representation = adaptation[n]['Representation']
                codec = adaptation[n]['@codecs'].split('.')[0]
                ano_codec = adaptation[n]['@codecs'].split('.')[0]
                rep_num = n
                ano_rep_num = n

        audio_info_dict = {}
        audio_there_num = 0
        if len(representation) < len(ano_representation):
            no_ids = len(ano_representation)
        else:
            no_ids = len(representation)
        for n in range(no_ids):
            try:
                ids = str(representation[n]['@id'])
            except IndexError:
                ids = ''
            ano_ids = str(ano_representation[n]['@id'])
            try:
                size = str(round(int(representation[n]['@bandwidth']) / 1000))
                if int(size) > 1024:
                    size = str(round(int(size) / 1024, 1)) + 'GB'
                else:
                    size += 'MB'
            except IndexError:
                size = ''
            ano_size = str(round(int(ano_representation[n]['@bandwidth']) / 1000))
            if int(ano_size) > 1024:
                ano_size = str(round(int(ano_size) / 1024, 1)) + 'GB'
            else:
                ano_size += 'MB'
            if ids == '' or size == '':
                new_dict = {
                    int(ano_ids.split('=')[-1]) + audio_there_num: [ano_ids, ano_codec, ano_size, "AUDIO"]
                }
            else:
                new_dict = {
                    int(ano_ids.split('=')[-1]) + audio_there_num: [ano_ids, ano_codec, ano_size, "AUDIO"],
                    int(ids.split('=')[-1]) + audio_there_num: [ids, codec, size, "AUDIO"],
                }
            audio_info_dict.update(new_dict)
            audio_there_num += 1

        myKeys = list(audio_info_dict.keys())
        myKeys.sort()
        audio_info_dict = {i: audio_info_dict[i] for i in myKeys}
        audio_keys = list(audio_info_dict.keys())

        if arguments.no_video is not None:
            tablee = prettytable.PrettyTable()
            tablee.field_names = [Fore.RED + "ID" + Fore.RESET, Fore.RED + "BITRATE" + Fore.RESET,
                                  Fore.RED + "CODEC" + Fore.RESET,
                                  Fore.RED + "TYPE" + Fore.RESET]
            tablee.align[Fore.RED + "BITRATE" + Fore.RESET] = "l"

            for a_num in range(len(list(audio_info_dict))):
                a_bitrate = audio_info_dict[list(audio_info_dict)[a_num]][0].split('=')[-1]
                a_codec = audio_info_dict[list(audio_info_dict)[a_num]][1]
                a_type = audio_info_dict[list(audio_info_dict)[a_num]][3]
                tablee.add_row([Fore.GREEN + f"{a_num+1}" + Fore.RESET, Fore.YELLOW + a_bitrate + Fore.RESET, Fore.LIGHTWHITE_EX + a_codec + Fore.RESET,
                                Fore.LIGHTBLACK_EX + a_type + Fore.RESET])
            print()
        if arguments.no_video is not None and arguments.audio_quality is not None:
            for audio_br in list(audio_info_dict):
                if int(arguments.audio_quality) == round(int(audio_br)/1000):
                    audio_id_entered = int(list(audio_info_dict).index(audio_br))
                    break
                else:
                    audio_id_entered = False
            if audio_id_entered is False:
                print(Fore.RED + f'The Selected Audio Quality Does Not Exist' + Fore.RESET)
                exit()
            audio_id_dl = audio_info_dict[list(audio_info_dict)[audio_id_entered]][0]
        elif arguments.audio_quality is None and arguments.quality is None and arguments.no_video is True:
            print(tablee)
            audio_id_entered = int(input('\nEnter Audio ID: '))
            while audio_id_entered > len(list(audio_info_dict)):
                audio_id_entered = int(input('\nEnter Audio ID: '))
            audio_id_dl = audio_info_dict[list(audio_info_dict)[audio_id_entered-1]][0]
        else:
            audio_id_entered = False
            audio_id_dl = False

    def audio_segments_append(audio_id, rep_num, mpd_link):
        audio_segments = []
        d = 0
        global link
        global n
        for n in range(len(contents['MPD']['Period']['AdaptationSet'][rep_num]['SegmentTemplate']['SegmentTimeline']['S'])):
            link = mpd_link.split('index')[0] + '/dash/'
            if n == 0:
                link = link + media.replace('$RepresentationID$', audio_id).replace('-$Time$', '')
                audio_segments.append(link)
            elif n == 1:
                link = link + media.replace('$RepresentationID$', audio_id).replace('-$Time$', '-0')
                audio_segments.append(link)
            else:
                r = contents['MPD']['Period']['AdaptationSet'][rep_num]['SegmentTemplate']['SegmentTimeline']['S'][n - 2].get('@r')
                m = contents['MPD']['Period']['AdaptationSet'][rep_num]['SegmentTemplate']['SegmentTimeline']['S'][n - 2]['@d']
                if r is not None:
                    for num in range(int(r) + 1):
                        d = int(d) + int(m)
                        link = mpd_link.split('index')[0] + '/dash/'
                        link = link + media.replace('$RepresentationID$', audio_id).replace('$Time$', f'{d}')
                        audio_segments.append(link)

                else:
                    d = int(contents['MPD']['Period']['AdaptationSet'][rep_num]['SegmentTemplate']['SegmentTimeline']['S'][n - 2]['@d']) + int(d)
                    link = link + media.replace('$RepresentationID$', audio_id).replace('$Time$', f'{d}')
                    audio_segments.append(link)
                if n == len(contents['MPD']['Period']['AdaptationSet'][rep_num]['SegmentTemplate']['SegmentTimeline']['S']) - 1:
                    d = int(contents['MPD']['Period']['AdaptationSet'][rep_num]['SegmentTemplate']['SegmentTimeline']['S'][n - 1]['@d']) + int(d)
                    link = mpd_link.split('index')[0] + '/dash/'
                    link = link + media.replace('$RepresentationID$', audio_id).replace('$Time$', f'{d}')
                    audio_segments.append(link)
        return audio_segments

    def video_segments_append(videoid, repre):
        time_a = 0
        time = 0
        video_segments = []
        v_d = 0
        global link

        time_s = repre['SegmentTemplate']['SegmentTimeline']['S']
        if isinstance(time_s, list):
            if len(time_s) == 2:
                for nm in range(len(time_s)):
                    if time_s[nm].get('@r') is not None:
                        time = int(time_s[nm].get('@d'))
                        no_of_segments = int(time_s[nm].get('@r')) + 3
                        for n in range(no_of_segments):
                            link = MPD.split('index')[0] + 'dash/'
                            if n == 0:
                                link = link + media.replace('$RepresentationID$', videoid).replace('-$Time$', '')
                                video_segments.append(link)
                            elif n == 1:
                                link = link + media.replace('$RepresentationID$', videoid).replace('-$Time$', '-0')
                                video_segments.append(link)
                            else:
                                time_a = time_a + time
                                link = link + media.replace('$RepresentationID$', videoid).replace('$Time$', f'{time_a}')
                                video_segments.append(link)
            else:
                for n in range(len(time_s) + 2):
                    link = MPD.split('index')[0] + 'dash/'
                    if n == 0:
                        link = link + media.replace('$RepresentationID$', videoid).replace('-$Time$', '')
                        video_segments.append(link)
                    elif n == 1:
                        link = link + media.replace('$RepresentationID$', videoid).replace('-$Time$', '-0')
                        video_segments.append(link)
                    else:
                        r = time_s[n-2].get('@r')
                        m = time_s[n-2]['@d']
                        if r is not None:
                            for num in range(int(r)+1):
                                link = MPD.split('index')[0] + 'dash/'
                                v_d = int(v_d) + int(m)
                                link = link + media.replace('$RepresentationID$', videoid).replace('$Time$', f'{v_d}')
                                video_segments.append(link)

                        else:
                            link = MPD.split('index')[0] + 'dash/'
                            v_d = int(time_s[n-2]['@d']) + int(v_d)
                            link = link + media.replace('$RepresentationID$', videoid).replace('$Time$', f'{v_d}')
                            video_segments.append(link)
                        if n == len(time_s) - 1:
                            link = MPD.split('index')[0] + 'dash/'
                            v_d = int(time_s[n-1]['@d']) + int(v_d)
                            link = link + media.replace('$RepresentationID$', videoid).replace('$Time$', f'{v_d}')
                            video_segments.append(link)
                print()
        else:
            time = int(time_s.get('@d'))
            no_of_segments = int(time_s.get('@r')) + 3
            for n in range(no_of_segments):
                link = MPD.split('index')[0] + 'dash/'
                if n == 0:
                    link = link + media.replace('$RepresentationID$', videoid).replace('-$Time$', '')
                    video_segments.append(link)
                elif n == 1:
                    link = link + media.replace('$RepresentationID$', videoid).replace('-$Time$', '-0')
                    video_segments.append(link)
                else:
                    time_a = time_a + time
                    link = link + media.replace('$RepresentationID$', videoid).replace('$Time$', f'{time_a}')
                    video_segments.append(link)
        return video_segments

    for n in range(len(adaptation)):
        if '"3840"' and '"2160"' in r:
            if adaptation[n]['@contentType'] == 'video' and adaptation[n]['@maxWidth'] == '3840':
                representation = adaptation[n]['Representation']
                repre = adaptation[n]
                v_r_num = n
            elif adaptation[n]['@contentType'] == 'video':
                ano_representation = adaptation[n]['Representation']
                ano_repre = adaptation[n]
                a_v_r_num = n
        elif adaptation[n]['@contentType'] == 'video':
            representation = adaptation[n]['Representation']
            ano_representation = adaptation[n]['Representation']
            repre = adaptation[n]
            ano_repre = adaptation[n]
    video_info_dict = {}
    video_there_num = 0
    if len(ano_representation) > len(representation):
        v_id_try = len(ano_representation)
    else:
        v_id_try = len(representation)
    for n in range(v_id_try):
        try:
            width = int(representation[n]['@width'])
            height = int(representation[n]['@height'])
            ids = str(representation[n]['@id'])
            bitrate = str(round(int(representation[n]['@bandwidth']) / 1000)) + 'K'
            codec = str(representation[n]['@codecs'].split('.')[0])
        except IndexError:
            width = ''
            height = ''
            ids = ''
            bitrate = ''
            codec = ''
        ano_ids = str(ano_representation[n]['@id'])
        ano_width = int(ano_representation[n]['@width'])
        ano_height = int(ano_representation[n]['@height'])
        ano_bitrate = str(round(int(ano_representation[n]['@bandwidth']) / 1000)) + 'K'
        ano_codec = str(ano_representation[n]['@codecs'].split('.')[0])
        if ano_width in list(video_info_dict.keys()) or ano_width + video_there_num in list(video_info_dict):
            video_there_num += 1
        if width == '':
            new_dict = {
                ano_width + video_there_num: [ano_ids, ano_width, ano_height, ano_codec, ano_bitrate, "VIDEO", ano_repre]
            }
        else:
            if width in list(video_info_dict.keys()) or width + video_there_num in list(video_info_dict):
                video_there_num += 2
            new_dict = {
                ano_width + video_there_num: [ano_ids, ano_width, ano_height, ano_codec, ano_bitrate, "VIDEO", ano_repre],
                width + video_there_num: [ids, width, height, codec, bitrate, "VIDEO", repre],
            }
        video_info_dict.update(new_dict)

    if arguments.subs_only:
        pass
    elif arguments.no_video is True:
        pass
    else:
        tablee = prettytable.PrettyTable()
        tablee.field_names = [Fore.RED + "ID" + Fore.RESET, Fore.RED + "RESOLUTION" + Fore.RESET,
                              Fore.RED + "CODEC" + Fore.RESET, Fore.RED + "BITRATE" + Fore.RESET,
                              Fore.RED + "TYPE" + Fore.RESET]
        for le in tablee.field_names:
            tablee.align[le] = "l"
        myKeys = list(video_info_dict.keys())
        myKeys.sort()
        video_info_dict = {i: video_info_dict[i] for i in myKeys}
        key = list(video_info_dict.keys())
        for n in range(len(video_info_dict)):
            resolution = f'{video_info_dict[key[n]][1]}x{video_info_dict[key[n]][2]}'
            codec = video_info_dict[key[n]][3]
            v_br = video_info_dict[key[n]][4]
            file_type = video_info_dict[key[n]][5]
            tablee.add_row([Fore.GREEN + str(n + 1) + Fore.RESET, Fore.YELLOW + resolution + Fore.RESET,
                            Fore.LIGHTWHITE_EX + codec + Fore.RESET, Fore.GREEN + v_br + Fore.RESET,
                            Fore.LIGHTBLACK_EX + file_type + Fore.RESET])
        wanted_ids = []
        if arguments.no_video is not None:
            try:
                if int(arguments.audio_quality) >= 192:
                    for nber in range(len(list(video_info_dict.keys()))):
                        if dl_quality >= video_info_dict[list(video_info_dict.keys())[nber]][1]:
                            wanted_ids.append(list(video_info_dict.keys())[nber])
                            video_repres = video_info_dict[list(video_info_dict.keys())[nber]][-1]
                    video_id = video_info_dict[max(wanted_ids)][0]
                    video_quality = video_info_dict[max(wanted_ids)][2]
                    ID = int(list(video_info_dict.keys()).index(max(wanted_ids))) + 1
                    print()
                elif int(arguments.audio_quality) < 192:
                    video_id = video_info_dict[list(video_info_dict)[0]][0]
                    video_quality = video_info_dict[list(video_info_dict)[0]][2]
                    ID = int(list(video_info_dict.keys()).index(list(video_info_dict)[0])) + 1
                else:
                    print(tablee)
                    ID = int(input('\nEnter ID: '))
                    while ID not in range(len(key) + 1):
                        ID = int(input('\nEnter ID: '))
                    print()
                    video_id = video_info_dict[list(video_info_dict.keys())[ID - 1]][0]
                    video_repres = video_info_dict[list(video_info_dict.keys())[ID - 1]][-1]
                    video_quality = video_info_dict[list(video_info_dict.keys())[ID - 1]][2]
            except TypeError:
                if arguments.quality is not None:
                    for nber in range(len(list(video_info_dict.keys()))):
                        if dl_quality >= video_info_dict[list(video_info_dict.keys())[nber]][1]:
                            wanted_ids.append(list(video_info_dict.keys())[nber])
                            video_repres = video_info_dict[list(video_info_dict.keys())[nber]][-1]
                    video_id = video_info_dict[max(wanted_ids)][0]
                    video_quality = video_info_dict[max(wanted_ids)][2]
                    ID = int(list(video_info_dict.keys()).index(max(wanted_ids))) + 1
                    print()
                else:
                    print(tablee)
                    ID = int(input('\nEnter ID: '))
                    while ID not in range(len(key) + 1):
                        ID = int(input('\nEnter ID: '))
                    print()
                    video_id = video_info_dict[list(video_info_dict.keys())[ID - 1]][0]
                    video_repres = video_info_dict[list(video_info_dict.keys())[ID - 1]][-1]
                    video_quality = video_info_dict[list(video_info_dict.keys())[ID - 1]][2]
    if arguments.no_video is True and arguments.audio_quality is None:
        ID = len(list(video_info_dict.keys()))
        video_id = video_info_dict[list(video_info_dict.keys())[ID - 1]][0]
        video_repres = video_info_dict[list(video_info_dict.keys())[ID - 1]][-1]
        video_quality = video_info_dict[list(video_info_dict.keys())[ID - 1]][2]
        print()
    try:
        if int(video_quality) == 180:
            video_quality = 144
        elif int(video_quality) == 270:
            video_quality = 240
        elif int(video_quality) == 486:
            video_quality = 480
    except UnboundLocalError:
        pass

    def concatenate_segments(inputs_name, input_name):
        if 'audio' in input_name:
            if os.path.isfile(f'{main_dir}\\temp\\{dl_name} {input_name}.m4a'):
                os.remove(f'{main_dir}\\temp\\{dl_name} {input_name}.m4a')
            files = glob.glob(f'{main_dir}\\temp\\{inputs_name}\\*')
            files.sort(key=lambda f: int(re.sub('\D', '', f)))
            print()
            print(Fore.YELLOW + '\nConcatenating Segments . . .\n' + Fore.RESET)
            bar = IncrementalBar(Fore.YELLOW + 'Processing' + Fore.LIGHTBLUE_EX, max=int(len(files)),
                                 suffix='%(percent)d%%' + Fore.RESET)
            with open(f'{main_dir}\\temp\\{dl_name} {input_name}.m4a', 'wb') as destination:
                for file in files:
                    with open(file, 'rb') as source:
                        shutil.copyfileobj(source, destination)
                        bar.next()
        else:
            if os.path.isfile(f'{main_dir}\\temp\\{dl_name} {input_name}.mp4'):
                os.remove(f'{main_dir}\\temp\\{dl_name} {input_name}.mp4')
            files = glob.glob(f'{main_dir}\\temp\\{inputs_name}\\*')
            files.sort(key=lambda f: int(re.sub('\D', '', f)))
            print()
            print(Fore.YELLOW + '\nConcatenating Segments . . .\n' + Fore.RESET)
            bar = IncrementalBar(Fore.WHITE + 'Processing' + Fore.LIGHTBLUE_EX, max=int(len(files)),
                                 suffix='%(percent)d%%' + Fore.RESET)
            with open(f'{main_dir}\\temp\\{dl_name} {input_name}.mp4', 'wb') as destination:
                for file in files:
                    with open(file, 'rb') as source:
                        shutil.copyfileobj(source, destination)
                        bar.next()
        bar.finish()
        shutil.rmtree(f'{main_dir}\\temp\\{inputs_name}')
        print()
        print(Fore.GREEN + 'Done!' + Fore.RESET)
        print()

    def download_subs(mpd_url, name):

        if os.path.isfile(f'{main_dir}\\temp\\{name}.vtt'):
            os.remove(f'{main_dir}\\temp\\{name}.vtt')
        if os.path.isfile(f'{main_dir}\\temp\\{name}.srt'):
            os.remove(f'{main_dir}\\temp\\{name}.srt')

        for num in range(len(adaptation)):
            try:
                if adaptation[num]['@codecs'] == "wvtt":
                    sub_id = adaptation[num]["Representation"]["@id"]
                    seg_template = adaptation[num]["SegmentTemplate"]["@initialization"]
            except KeyError:
                pass
        sub_url = mpd_url.rsplit('/', 1)[0] + '/' + seg_template
        sub_url = sub_url.replace('_cenc_dash', '_hls').replace('$RepresentationID$', f'{sub_id}').replace('.dash?&', '.vtt')
        # url = url.replace('_cenc_dash', '_hls').replace('.dash', '.vtt')

        if arguments.subs_only:
            print()

        print(Fore.YELLOW + 'Downloading Subtitles . . .' + Fore.RESET)

        aria_cmd = [
            f'{main_dir}\\binaries\\aria2c.exe',
            '--max-tries=10',
            '--async-dns=false',
            '--check-certificate=false',
            '--enable-color=true',
            '--allow-overwrite=true',
            '--auto-file-renaming=false',
            '--file-allocation=prealloc',
            '--summary-interval=0',
            '--retry-wait=0',
            '--uri-selector=inorder',
            '--console-log-level=warn',
            '--download-result=hide',
            f'{sub_url}',
            f'-d {main_dir}\\temp\\',
            f'-o {name}.vtt'
        ]
        # print(aria_cmd)
        subprocess.run(aria_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            with open(f'{main_dir}\\temp\\{name}.vtt', mode='r', encoding='utf-8') as f:
                sub_contents = f.readlines()
        except FileNotFoundError:
            i = 0
            while i < 2:
                subprocess.run(aria_cmd)
                if os.path.isfile(f'{main_dir}\\temp\\{name}.vtt'):
                    with open(f'{main_dir}\\temp\\{name}.vtt', mode='r', encoding='utf-8') as f:
                        sub_contents = f.readlines()
                    break
                i += 1

        with open(f'{main_dir}\\temp\\{name}.srt', mode='w', encoding='utf-8') as i:
            num = 1
            for n in range(len(sub_contents)):
                if n > 2:
                    try:
                        int(sub_contents[n])
                    except ValueError:
                        try:
                            int(sub_contents[n][0:2])
                        except ValueError:
                            i.write(f'{sub_contents[n]}')
                        else:
                            i.write(f'{sub_contents[n].replace(".", ":")}')
                    else:
                        i.write(f'{num}\n')
                        num += 1
        os.remove(f'{main_dir}\\temp\\{name}.vtt')
        print(Fore.GREEN + '\nDone Downloading Subtitles!\n' + Fore.RESET)

    def download_segments(mpd_url, input_name, mode):
        # subprocess.run(f'"{main_dir}\\binaries\\aria2c.exe" "{mpd_url}" -o "{main_dir}"')
        if os.path.isdir(f'{main_dir}\\temp\\{input_name}'):
            shutil.rmtree(f'{main_dir}\\temp\\{input_name}')
        txt_name = mpd_url.rsplit('/', 2)[-2].split('.')[0] + input_name
        if os.path.isfile(f'{main_dir}\\temp\\{txt_name}.txt'):
            os.remove(f'{main_dir}\\temp\\{txt_name}.txt')
        if os.path.isfile(f'{main_dir}\\temp\\{txt_name}.txt'):
            os.makedirs(f'{main_dir}\\temp\\{txt_name}.txt')
        for each_link in mode:
            with open(f'{main_dir}\\temp\\{txt_name}.txt', mode='a+') as f:
                f.write(each_link + '\n')
        if 'audio' in mode[0]:
            print(Fore.YELLOW + f'Downloading {round(int(input_name.split("=")[-1])/1000)} Kbps Audio . . .' + Fore.RESET)
        else:
            print(Fore.YELLOW + f'Downloading {video_quality}p Video . . .' + Fore.RESET)
        print()
        aria2c_cmd = [
            f'{main_dir}\\binaries\\aria2c.exe',
            f'-i {main_dir}\\temp\\{txt_name}.txt',
            '-x16', '-j16', '-k1M', '-s16',
            '--async-dns=false',
            '--check-certificate=false',
            '--enable-color=true',
            '--allow-overwrite=true',
            '--auto-file-renaming=false',
            '--file-allocation=prealloc',
            '--summary-interval=0',
            '--retry-wait=5',
            '--uri-selector=inorder',
            '--console-log-level=warn',
            '--download-result=hide',
            '--max-tries=0',
            f'-d {main_dir}\\temp\\{input_name}'
        ]
        subprocess.run(aria2c_cmd)
        temp_c = os.listdir(f'{main_dir}\\temp\\{input_name}\\')
        missed_segments = []
        if len(temp_c) != len(mode):
            for nmb in range(len(mode)):
                temp_c = os.listdir(f'{main_dir}\\temp\\{input_name}\\')
                if mode[nmb].rsplit("/", 1)[-1] not in temp_c:
                    missed_segments.append(mode[nmb])
            with open(f'{main_dir}\\temp\\missed.txt', mode='w') as ms_links:
                for ms_link in missed_segments:
                    ms_links.write(f'{ms_link}\n')
            aria2c_cmd = [
                f'{main_dir}\\binaries\\aria2c.exe',
                f'-i {main_dir}\\temp\\missed.txt',
                '-x16', '-j30', '-k1M', '-s16',
                '--async-dns=false',
                '--check-certificate=false',
                '--enable-color=true',
                '--allow-overwrite=true',
                '--auto-file-renaming=false',
                '--file-allocation=prealloc',
                '--summary-interval=0',
                '--retry-wait=5',
                '--uri-selector=inorder',
                '--console-log-level=warn',
                '--download-result=hide',
                '--max-tries=0',
                f'-d {main_dir}\\temp\\{input_name}'
            ]
            subprocess.run(aria2c_cmd)
            os.remove(f'{main_dir}\\temp\\missed.txt')
        os.remove(f'{main_dir}\\temp\\{txt_name}.txt')

    if not arguments.subs_only:

        if int(list(video_info_dict.keys())[ID - 1]) > 1900:
            if not arguments.no_audio:
                if audio_id_dl:
                    audio_id = audio_id_dl
                    audio_to_dl = list(audio_info_dict)[audio_id_entered-1]
                else:
                    audio_to_dl = max(audio_keys)
                    audio_id = audio_info_dict[audio_to_dl][0]
                audio_segments = audio_segments_append(audio_id=audio_id, rep_num=rep_num, mpd_link=MPD)
                download_segments(mpd_url=MPD, input_name=audio_id, mode=audio_segments)
                concatenate_segments(inputs_name=audio_id, input_name=audio_id)
                audio_to_dl = audio_keys[2]
                if arguments.audio_quality is None:
                    if not audio_to_dl == max(audio_keys):
                        audio_id = audio_info_dict[audio_to_dl][0]
                        audio_segments = audio_segments_append(audio_id=audio_id, rep_num=ano_rep_num, mpd_link=MPD)
                        download_segments(mpd_url=MPD, input_name=audio_id, mode=audio_segments)
                        concatenate_segments(inputs_name=audio_id, input_name=audio_id)
            if not arguments.no_video:
                video_segments = video_segments_append(videoid=video_id, repre=video_repres)
                download_segments(mpd_url=MPD, input_name=video_id, mode=video_segments)
                concatenate_segments(inputs_name=video_id, input_name=video_id)
        elif 1200 < int(list(video_info_dict.keys())[ID - 1]) < 1900:
            if not arguments.no_audio:
                try:
                    audio_to_dl = audio_keys[2]
                    audio_id = audio_info_dict[audio_to_dl][0]
                except IndexError or KeyError:
                    audio_to_dl = audio_keys[1]
                    audio_id = audio_info_dict[audio_to_dl][0]
                audio_segments = audio_segments_append(audio_id=audio_id, rep_num=ano_rep_num, mpd_link=MPD)
                download_segments(mpd_url=MPD, input_name=audio_id, mode=audio_segments)
                concatenate_segments(inputs_name=audio_id, input_name=audio_id)
            if not arguments.no_video:
                video_segments = video_segments_append(videoid=video_id, repre=video_repres)
                download_segments(mpd_url=MPD, input_name=video_id, mode=video_segments)
                concatenate_segments(inputs_name=video_id, input_name=video_id)
        else:
            if not arguments.no_audio:
                audio_to_dl = audio_keys[0]
                audio_id = audio_info_dict[audio_to_dl][0]
                audio_segments = audio_segments_append(audio_id=audio_id, rep_num=ano_rep_num, mpd_link=MPD)
                download_segments(mpd_url=MPD, input_name=audio_id, mode=audio_segments)
                concatenate_segments(inputs_name=audio_id, input_name=audio_id)
            if not arguments.no_video:
                video_segments = video_segments_append(videoid=video_id, repre=video_repres)
                download_segments(mpd_url=MPD, input_name=video_id, mode=video_segments)
                concatenate_segments(inputs_name=video_id, input_name=video_id)
    try:
        download_subs(mpd_url=MPD, name=dl_name)
    except UnboundLocalError:
        print(Fore.RED + 'No Subtitles Available . . .\n' + Fore.RESET)
        if arguments.subs_only and catalogType == 'movie':
            exit()


def deceryptAndMerge(name, mp4decrypt_keys, language):
    videos_num = 0
    audios_num = 0
    subs_num = 0
    MTN_order = []
    videos_names = []
    audios_names = []
    subs_names = []
    MTN_Video_args = ""
    MTN_Audio_args = ""
    MTN_Subs_args = ""

    temp_dec_pre_contents = os.listdir(f'{main_dir}\\temp\\')

    for dec_c in temp_dec_pre_contents:
        if '.mp4' in dec_c and name in dec_c and '[DEC]' in dec_c:
            os.remove(f'{main_dir}\\temp\\{dec_c}')
        elif '.m4a' in dec_c and name in dec_c and '[DEC]' in dec_c:
            os.remove(f'{main_dir}\\temp\\{dec_c}')

    for n in range(len(os.listdir(os.curdir + f'/temp/'))):
        if '.mp4' in os.listdir(os.curdir + f'/temp/')[n] and name in os.listdir(os.curdir + f'/temp/')[n]:
            videos_names.append(os.listdir(os.curdir + f'/temp/')[n])
            videos_num += 1
        if '.m4a' in os.listdir(os.curdir + f'/temp/')[n] and name in os.listdir(os.curdir + f'/temp/')[n]:
            audios_names.append(os.listdir(os.curdir + f'/temp/')[n])
            audios_num += 1
        if f'{name}.srt' in os.listdir(os.curdir + f'/temp/')[n]:
            subs_names.append(os.listdir(os.curdir + f'/temp/')[n])
            subs_num += 1

    for n in range(videos_num + audios_num + subs_num):
        MTN_order.append(str(f'{n}:0'))

    MTN_order = ",".join(MTN_order)

    def decryptVideoandAudio():
        dec_video_names = []
        dec_audio_names = []
        for n in range(videos_num):
            print(Fore.YELLOW + 'Decrypting Video . . .' + Fore.RESET)
            subprocess.run(
                f'binaries/mp4decrypt.exe --show-progress {mp4decrypt_keys} "{main_dir}/temp/{videos_names[n]}" "{main_dir}/temp/{videos_names[n].split(".mp4")[0].title()} [DEC].mp4"',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(Fore.GREEN + '\nDone Decrypting Video . . .\n' + Fore.RESET)
            dec_video_names.append(f'{videos_names[n].split(".mp4")[0].title()} [DEC]')
            os.remove(f'{main_dir}/temp/{videos_names[n]}')
        for n in range(audios_num):
            print(Fore.YELLOW + '\nDecrypting Audio . . .' + Fore.RESET)
            subprocess.run(
                f'binaries/mp4decrypt.exe --show-progress {mp4decrypt_keys} "{main_dir}/temp/{audios_names[n]}" "{main_dir}/temp/{audios_names[n].split(".m4a")[0].title()} [DEC].m4a"',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(Fore.GREEN + '\nDone Decrypting Audio . . .' + Fore.RESET)
            dec_audio_names.append(f'{audios_names[n].split(".m4a")[0].title()} [DEC]')
            os.remove(f'{main_dir}/temp/{audios_names[n]}')

        return dec_audio_names, dec_video_names

    audio_dec_names, video_dec_names = decryptVideoandAudio()
    dem_audio_names = []
    dem_video_names = []

    if audio_dec_names:
        dem_audio_names = (demux(dem_input=audio_dec_names, dem_mode='audio'))[1]
    if video_dec_names:
        dem_video_names = (demux(dem_input=video_dec_names, dem_mode='video'))[0]

    if arguments.no_video:
        pass
    elif arguments.no_audio:
        pass
    elif arguments.subs_only:
        pass
    else:
        data = getMediaInfo(videos_names=dem_video_names, audios_names=dem_audio_names, language=language)
        for n in range(videos_num):
            MTN_Video_args = MTN_Video_args + f' --language 0:und "{main_dir}/temp/{dem_video_names[n]}" '
        for n in range(audios_num):
            MTN_Audio_args = MTN_Audio_args + f'--language 0:{language} "{main_dir}/temp/{dem_audio_names[n]}" '
        for n in range(subs_num):
            MTN_Subs_args = MTN_Subs_args + f'--language 0:en --track-name "0:English" "{main_dir}/temp/{subs_names[n]}" '

        if subs_num != 0:
            subs_in_name = '-ESub'
        else:
            subs_in_name = ''

        final_name = f'{name} {data}{subs_in_name}'.replace('  ', ' ')
        final_name = final_name.replace(' ', '.')
        final_name_1 = final_name.replace('.-.', '-')
        if arguments.GROUP != '':
            final_name = final_name_1 + f'-{arguments.GROUP}'
        else:
            final_name = final_name_1

        MTN_Args = '--ui-language en --priority lower --no-date ' + f'--output "{main_dir}/downloads/{final_name}.mkv"' + MTN_Video_args + MTN_Audio_args + f'--title "{final_name_1}" ' + MTN_Subs_args + f'--track-order {MTN_order}'

        print(Fore.YELLOW + '\nMuxing Video and Audio . . .' + Fore.RESET)

        subprocess.run(f'"{mkvmergeexe}" {MTN_Args}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(Fore.GREEN + '\nDone Muxing Video and Audio . . .' + Fore.RESET)
        try:
            for video in dem_video_names:
                os.remove(f'{main_dir}\\temp\\{video}')
            for audio in dem_audio_names:
                os.remove(f'{main_dir}\\temp\\{audio}')
            os.remove(f'{main_dir}\\temp\\{name}.srt')
        except FileNotFoundError:
            pass


def getMediaInfo(videos_names, audios_names, language):
    mediainfo = subprocess.run(f'"{mediainfoexe}" --Output=JSON "{main_dir}/temp/{videos_names[0]}"', stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    mediainfo = mediainfo.stdout.decode()
    mediainfo = json.loads(mediainfo)

    for n in range(len(mediainfo['media']['track'])):
        try:
            video_codec = mediainfo['media']['track'][n]['Format']
            video_width = int(mediainfo['media']['track'][n]['Width'])
        except KeyError:
            pass
    if video_codec.lower() == 'avc':
        v_codec = 'x264'
    elif video_codec.lower() == 'hevc':
        v_codec = 'x265'
    else:
        v_codec = 'Unknown'
    if video_width < 1000:
        v_quality = 'HQ'
    elif video_width > 1001 and video_width < 1900:
        v_quality = '720p'
    elif video_width > 1901 and video_width < 2500:
        v_quality = '1080p'
    elif video_width > 2501 and video_width < 4000:
        v_quality = '2160p'
    else:
        v_quality = '8K'

    mediainfo = subprocess.run(f'"{mediainfoexe}" --Output=JSON "{main_dir}/temp/{audios_names[0]}"', stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    mediainfo = mediainfo.stdout.decode()
    mediainfo = json.loads(mediainfo)

    for n in range(len(mediainfo['media']['track'])):
        try:
            audio_codec = mediainfo['media']['track'][n]['Format']
            audio_bitrate = round(int(mediainfo['media']['track'][n]['BitRate']) / 1000)
            audio_channels = mediainfo['media']['track'][n]['Channels']
        except KeyError:
            pass
    if audio_codec.lower() != 'aac':
        audio_codec = 'DD+'
    if audio_bitrate == 64 or audio_bitrate == 96:
        a_bitrate = ''
    else:
        a_bitrate = f' - {audio_bitrate} Kbps'
    if audio_channels == '6':
        a_channels = '5.1'
    elif audio_channels == '8':
        a_channels = '7.1'
    else:
        a_channels = '2.0'
    if language.lower() == 'te':
        a_lang = 'Telugu'
    elif language.lower() == 'kn' or language.lower() == 'kan':
        a_lang = 'Kannada'
    elif language.lower() == 'ta' or language.lower() == 'tam':
        a_lang = 'Tamil'
    else:
        a_lang = 'English'
    data = f'{v_quality} {mode} WEB-DL {v_codec} [{a_lang} ({audio_codec} {a_channels}{a_bitrate})]'
    if len(audios_names) == 2:

        mediainfo = subprocess.run(f'"{mediainfoexe}" --Output=JSON "{main_dir}/temp/{audios_names[1]}"',
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mediainfo = mediainfo.stdout.decode()
        mediainfo = json.loads(mediainfo)

        for n in range(len(mediainfo['media']['track'])):
            try:
                audio_codec_1 = mediainfo['media']['track'][n]['Format']
                audio_bitrate_1 = round(int(mediainfo['media']['track'][n]['BitRate']) / 1000)
                audio_channels_1 = mediainfo['media']['track'][n]['Channels']
            except KeyError:
                pass
        if audio_codec_1.lower() != 'aac':
            audio_codec_1 = 'DD+'
        if audio_bitrate_1 == 64 or audio_bitrate_1 == 96:
            a_bitrate_1 = ''
        else:
            a_bitrate_1 = f' - {audio_bitrate_1} Kbps'
        if audio_channels_1 == '6':
            a_channels_1 = '5.1'
        elif audio_channels_1 == '8':
            a_channels_1 = '7.1'
        else:
            a_channels_1 = '2.0'
        if audio_codec == audio_codec_1:
            data = f'{v_quality} {mode} WEB-DL {v_codec} [{a_lang} ({audio_codec} {a_channels}{a_bitrate})]'
        elif audio_codec_1.lower() == 'aac':
            data = f'{v_quality} {mode} WEB-DL {v_codec} [{a_lang} ({audio_codec} {a_channels}{a_bitrate} & {audio_codec_1} {a_channels_1})]'
        else:
            data = f'{v_quality} {mode} WEB-DL {v_codec} [{a_lang} ({audio_codec_1} {a_channels_1}{a_bitrate_1} & {audio_codec} {a_channels})]'

    return data


def gen_x_device_id():
    global authorization
    global x_authorization
    global deviceID

    headers = {
        'authority': 'device-register-service.api.aha.firstlight.ai',
        'authorization': authorization,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        'x-client-id': 'firstlight-main-iosmobile',
        'x-authorization': x_authorization,
    }
    try:
        response = requests.post(url='https://device-register-service.api.aha.firstlight.ai/device/app/register',
                                 headers=headers, data='{"uniqueId":"' + deviceID + '"}')

    except requests.exceptions.ConnectionError:
        response = requests.post(url='https://device-register-service.api.aha.firstlight.ai/device/app/register',
                                 headers=headers, data='{"uniqueId":"' + deviceID + '"}')

    secret = json.loads(response.content)['data']['secret']
    servertime = int(json.loads(response.content)['header']['system_time'])
    jwttime = (servertime) / 1000

    x_device_id = jwt.encode({
        "deviceId": deviceID,
        "aud": "playback-auth-service",
        "iat": jwttime,
        "exp": jwttime + 30
    }, base64.b64decode(secret), algorithm="HS256")

    return x_device_id


def demux(dem_input, dem_mode):
    dem_video_names = []
    dem_audio_names = []
    for dem_num in range(len(dem_input)):
        if dem_mode == 'video':
            print(Fore.YELLOW + '\nDemuxing Video . . .' + Fore.RESET)
            dem_name = dem_input[dem_num].split("=")[0] + f' [DEM]'
            dem_video_names.append(f'{dem_name}.mp4')
            ffmpeg_cmd = [
                f'{ffmpeg_path}',
                '-i',
                fr'{main_dir}\\temp\\{dem_input[dem_num]}.mp4',
                '-c', 'copy',
                fr'{main_dir}\\temp\\{dem_name}.mp4',
                "-vn", "-sn", "-y", "-hide_banner", "-loglevel", "panic"
            ]
            subprocess.run(ffmpeg_cmd)
            try:
                os.remove(f'{main_dir}\\temp\\{dem_input[dem_num]}.mp4')
            except FileNotFoundError:
                pass
            print(Fore.GREEN + '\nDone Demuxing Video!' + Fore.RESET)
        elif dem_mode == 'audio':
            try:
                audio_br = dem_input[dem_num].split('=')[-1].split(" ")[0].strip()
                name = dem_input[dem_num].rsplit("_", 1)[0] + f' {round(int(audio_br)/1000)}K [DEM]'
                dem_input_name = f"{main_dir}\\temp\\{dem_input[dem_num]}.m4a"
                if round(int(audio_br)/1000) > 190:
                    ext = '.eac3'
                else:
                    ext = '.m4a'
                output_name = f"{main_dir}\\temp\\{name}{ext}"
                dem_audio_names.append(f'{name}{ext}')
                print(Fore.YELLOW + '\nDemuxing Audio . . .' + Fore.RESET)
                ffmpeg_cmd = [
                    f"{ffmpeg_path}",
                    f"-i",
                    fr'{dem_input_name}',
                    "-c:a",
                    "copy",
                    fr"{output_name}",
                    "-vn", "-sn", "-y", "-hide_banner", "-loglevel", "panic"
                ]
                subprocess.call(ffmpeg_cmd)
                try:
                    os.remove(f'{main_dir}\\temp\\{dem_input[dem_num]}.m4a')
                except FileNotFoundError:
                    pass
                print(Fore.GREEN + '\nDone Demuxing Audio . . .' + Fore.RESET)
            except ValueError:
                pass
        else:
            pass
    return dem_video_names, dem_audio_names


# try:
if not arguments.url:
    link = input('Enter AHA Link: ')
else:
    link = arguments.url
try:
    authorization, x_auth, x_device_id, deviceID, x_authorization = get_auths()
except requests.exceptions.ConnectionError:
    authorization, x_auth, x_device_id, deviceID, x_authorization = get_auths()
if 'webepisode' in link:
    catalogType = 'webepisode'
    getMPDs(link)
elif 'movie' in link:
    catalogType = 'movie'
    getMPDs(link)
else:
    print(Fore.LIGHTRED_EX + '\nTry Again...\nYou Did Not Enter a Valid Movie Or Episode Link...' + Fore.RESET)
# except:
#     print(Fore.LIGHTRED_EX + '\nAn Error Occured, Try again later...' + Fore.RESET)
