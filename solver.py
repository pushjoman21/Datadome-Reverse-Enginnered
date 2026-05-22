import tls_client
import json
import urllib.parse

from builder import build_payload
from crypto import encrypt

def solve(site="https://www.etsy.com/", ddjskey="D013AA612AB2224D03B2318D0F5B19", cid=""):

    session = tls_client.Session(client_identifier="chrome")

    payload_json = build_payload(profile="chrome_win10",
                                 url=site,
                                 tags_js_url=None,
                                 server_hash=None,
                                 bpc=1)
    
    #print(payload_json)

    referer_encoded = urllib.parse.quote(site, safe='')
    payload = encrypt(payload_json, ddjskey=ddjskey, cid=cid)

    #print(payload)

    headers = {
        'accept': '*/*',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'downlink': '10',
        'dpr': '1',
        'ect': '4g',
        'origin': 'https://www.etsy.com',
        'priority': 'u=1, i',
        'referer': 'https://www.etsy.com/',
        'rtt': '0',
        'sec-ch-dpr': '1',
        'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version-list': '"Chromium";v="148.0.7778.179", "Google Chrome";v="148.0.7778.179", "Not/A)Brand";v="99.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"14.0.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    }

    data = {
        'jspl': payload,
        'eventCounters': '[]',
        'jsType': 'ch',
        'cid': cid,
        'ddk': ddjskey,
        'Referer': referer_encoded,
        'request': '%2F',
        'responsePage': 'origin',
        'ddv': '5.6.6',
    }

    response = session.post('https://www.etsy.com/include/tags.js', headers=headers, data=data).json()

    if response["status"] == 200:
        datadome_cookie = response["cookie"]
        print(f"Solved Datadome [{datadome_cookie}]")


solve()
