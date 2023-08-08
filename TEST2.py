import requests
import json

APP_KEY = "PSM9hB6QskUJju5b2ZnswSNfyBLuN7bwNT6C"
APP_SECRET = "er9i/53546V3MMu8RfnFuVkVPsChL2bMlfOTQMTPmC6IAJc++Do5qhHFTzngUmk+axlQEGhNnCsr55Kchdf/61caICocHv7Sn9yQy2g0NPPBCFhLIWtlYp9nB6374l4AADNLfdpbrybEYxlWzN/KTwYtqvZcKVvipPfdhBZ2ck7ZJuXJCgU="
URL_BASE = "https://openapivts.koreainvestment.com:29443" #모의투자서비스

headers = {"content-type":"application/json"}
body = {"grant_type":"client_credentials",
        "appkey":APP_KEY,
        "appsecret":APP_SECRET}


PATH = "oauth2/tokenP"
URL = f"{URL_BASE}/{PATH}"

res = requests.post(URL, headers=headers, data=json.dumps(body))
ACCESS_TOKEN ="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjQzZWEwMTZlLTJmOTktNGMzOS1hM2VjLTNiY2IxYWE3ZWFlNyIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg3NjExNDU4LCJpYXQiOjE2ODc1MjUwNTgsImp0aSI6IlBTTTloQjZRc2tVSmp1NWIyWm5zd1NOZnlCTHVON2J3TlQ2QyJ9.8U0myThGUL-blcs8vr8tkF1gNCxbx5H40hc_1XtmkWyvtaQaR3twhf_GiKClbOxYnNCedBtdwj_iPriNbs_pXg"
print(ACCESS_TOKEN)

