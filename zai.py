# -*- coding: utf-8 -*-
# Module: ZEE5 RIPPER
# Created on: 11-10-2021
# Authors: Tej
# Version: 1.0.0

import base64, requests, sys, xmltodict
import index
from pywidevine.cdm import cdm, deviceconfig
from base64 import b64encode
from pywidevine.getPSSH import get_pssh
from pywidevine.decrypt.wvdecryptcustom import WvDecrypt

index = index.Zee5
index.login()
index.manifest()

mpd_url = getattr(index, 'mpd_url')
print('MPD URL: ', mpd_url)
pssh = getattr(index, 'pssh')
print('PSSH: ',pssh)
nl = getattr(index , 'nl')
sdrm = getattr(index ,'sdrm')
lic_url = "https://spapi.zee5.com/widevine/getLicense"
headers = {
          'nl': f'{nl}',
          'customdata': f'{sdrm}'
          }
def WV_Function(pssh, lic_url, cert_b64=None):
    #proxy = {

    #'https':'https://SU2TuiBYWmMoNiNYPWuv2YXT:s799YY2jGXzHSWmWLJJQ5bye@in123.nordvpn.com:89'

         #   }
    wvdecrypt = WvDecrypt(init_data_b64=pssh, cert_data_b64=cert_b64, device=deviceconfig.device_lenovolvl1)                   
    widevine_license = requests.post(url=lic_url, data=wvdecrypt.get_challenge(), headers=headers) #proxies=proxy
    license_b64 = b64encode(widevine_license.content)
    wvdecrypt.update_license(license_b64)
    Correct, keyswvdecrypt = wvdecrypt.start_process()
    if Correct:
        return Correct, keyswvdecrypt   
correct, keys = WV_Function(pssh, lic_url)

print()
for key in keys:
    print('--key ' + key)
