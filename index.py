import requests
import base64, requests, sys, xmltodict,json
import argparse
from pywidevine.cdm import cdm, deviceconfig
from base64 import b64encode
from pywidevine.getPSSH import get_pssh
from pywidevine.decrypt.wvdecryptcustom import WvDecrypt

arguments = argparse.ArgumentParser()
arguments.add_argument("-id", '--id', dest="id", help="content id")
args = arguments.parse_args()

content_id = args.id
class Zee5:
      def __init__(self):
         self.access_token = None
         self.id = f'{content_id}'
         self.mpd_url = None
         self.pssh = None #get_pssh(self.mpd_url)
         self.lic_url = "https://spapi.zee5.com/widevine/getLicense"
         self.nl = None
         self.sdrm = None
         
        
      
      def login(self):
         headers = {
    'authority': 'whapi.zee5.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    'accept': 'application/json',
    # Already added when you pass json=
    # 'content-type': 'application/json',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://www.zee5.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.zee5.com/',
    'accept-language': 'en-US,en;q=0.9',
    }

         json_data = {
    'email': 'gurramakshayreddy@gmail.com',
    'password': 'Modapps@430',
    'aid': '',
    'lotame_cookie_id': '',
    'guest_token': 'JXgOUk1zqE4MRvdpB2Q9000000000000',
    'platform': 'web',
    'version': '2.51.26',
    }
         #proxy ={ 
             #'https': 'https://SU2TuiBYWmMoNiNYPWuv2YXT:s799YY2jGXzHSWmWLJJQ5bye@in123.nordvpn.com:89'
       # }    
         res = requests.post('https://whapi.zee5.com/v1/user/loginemail_v2.php', headers=headers, json=json_data) #proxies=proxy
         self.access_token = res.json()['access_token']
         #print(res.json())
         #print(self.access_token)
         
      def manifest(self):
         headers = {
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
         }
         params = {
           'content_id': f'{self.id}',
           'device_id': '17fe8b24e576ec-0156d120ac0e84-26426a12-53c31-17fe8b24e587e4',
           'platform_name': 'mobile_web',
           'translation': 'en',
           'user_language': 'en,hi,te',
           'country': 'IN',
           'state': 'MH',
           'app_version':'2.51.26',
           'user_type': 'premium',
           'check_parental_control': 'false',
           'gender': 'Male',
           'age_group': '18-24',
           'uid': '9a275c26-71c6-46bb-b3a5-952a8f6a61db',
           'ppid': 'JXgOUk1zqE4MRvdpB2Q9000000000000',
           'version': '12'
         } 
         json_data = {
            'x-access-token': 'eyJ0eXAiOiJqd3QiLCJhbGciOiJIUzI1NiJ9.eyJwcm9kdWN0X2NvZGUiOiJ6ZWU1QDk3NSIsInBsYXRmb3JtX2NvZGUiOiJXZWJAJCF0Mzg3MTIiLCJpc3N1ZWRBdCI6IjIwMjItMDctMDZUMDY6MzA6MDIrMDAwMCIsInR0bCI6ODY0MDB9.R_U-gSYEYYY8vaVIpLfnoqQ7_q-V3KdtnH4L-bQrs6A',
            'Authorization': f'bearer {self.access_token}'      
         }
         #proxy = {
    #'https':'https://SU2TuiBYWmMoNiNYPWuv2YXT:s799YY2jGXzHSWmWLJJQ5bye@in123.nordvpn.com:89'
           # }
         res = requests.post('https://spapi.zee5.com/singlePlayback/getDetails/secure',headers = headers,params = params ,json=json_data) #proxies=proxy
         #print(res.json())
         dicto = res.json()
         json_file = json.dumps(dicto, indent = 4)
         with open('manifest.json', 'w') as outfile:
             outfile.write(json_file)
         self.nl = res.json()['keyOsDetails']['nl']
         self.sdrm = res.json()['keyOsDetails']['sdrm']
         self.mpd_url = res.json()['assetDetails']['video_url']['mpd']
         #print(self.mpd_url)
         self.pssh = get_pssh(self.mpd_url)
         #print(self.pssh)
        
      def device_id(self):
            headers = {
                      'authorization': self.access_token,
                      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
            }
            params = {
    'name': 'WebBrowser',
    'identifier': '17fe8b24e576ec-0156d120ac0e84-26426a12-53c31-17fe8b24e587e4',
}

            json_data = {
    'name': 'WebBrowser',
    'identifier': '17fe8b24e576ec-0156d120ac0e84-26426a12-53c31-17fe8b24e587e4',
}
           # proxy = {
    #'https':'https://SU2TuiBYWmMoNiNYPWuv2YXT:s799YY2jGXzHSWmWLJJQ5bye@in123.nordvpn.com:89'
           # }
            res = requests.post('https://subscriptionapi.zee5.com/v1/device', headers=headers, params=params, json=json_data) #proxies=proxy
            print(res.json())

       
         
         
         
         
         
         
         
Zee5 = Zee5()
Zee5.login()
Zee5.manifest()

      
      
      
      
   
