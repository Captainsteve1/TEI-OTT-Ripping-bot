# -*- coding: utf-8 -*-
import os
'''
w = open('config.json', 'w+')
w.write('{')
w.write('\n')
w.write('    "authToken": "'+os.getenv('BOT_TOKEN')+'",')
w.write('\n')
w.write('    "owner": '+os.getenv('OWNER_ID'))
w.write('\n')
w.write('}')
'''
from pywidevine.cdm import deviceconfig

CDM_DEVICE = deviceconfig.device_lenovolvl1

UA = 'okhttp/2.5.0'

KEY_FILE = 'client_key.json'
SUBS_FILE = 'subs'

# use this for device registration which will generate a client key that lasts
# for 6 months
INIT_AES_SECRET = b'A3s68aORSgHs$71P'
CLIENT_SECRET = 'apalyaSonyTV'

REGISTER_DEVICE_URL = 'https://api.sunnxt.com/user/v7/registerDevice'
CODE_URL = 'https://api.sunnxt.com/user/v4/device/code'
LINK_URL = 'https://api.sunnxt.com/user/v4/device/validate'
MEDIA_URL = 'https://api.sunnxt.com/content/v3/media/{}/'
LICENSE_URL = 'https://api.sunnxt.com/licenseproxy/v3/modularLicense/'

PRESETS = [1080, 720]
