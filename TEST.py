import json
import requests
import dollar_future_fuction as dff

APP_KEY = "PSM9hB6QskUJju5b2ZnswSNfyBLuN7bwNT6C"
APP_SECRET = "er9i/53546V3MMu8RfnFuVkVPsChL2bMlfOTQMTPmC6IAJc++Do5qhHFTzngUmk+axlQEGhNnCsr55Kchdf/61caICocHv7Sn9yQy2g0NPPBCFhLIWtlYp9nB6374l4AADNLfdpbrybEYxlWzN/KTwYtqvZcKVvipPfdhBZ2ck7ZJuXJCgU="
ACCESS_TOKEN ="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjQzZWEwMTZlLTJmOTktNGMzOS1hM2VjLTNiY2IxYWE3ZWFlNyIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg3NjExNDU4LCJpYXQiOjE2ODc1MjUwNTgsImp0aSI6IlBTTTloQjZRc2tVSmp1NWIyWm5zd1NOZnlCTHVON2J3TlQ2QyJ9.8U0myThGUL-blcs8vr8tkF1gNCxbx5H40hc_1XtmkWyvtaQaR3twhf_GiKClbOxYnNCedBtdwj_iPriNbs_pXg"
URL_BASE = "https://openapivts.koreainvestment.com:29443" #모의투자서비스

body = {"grant_type":"client_credentials",
        "appkey":"PSM9hB6QskUJju5b2ZnswSNfyBLuN7bwNT6C",
        "appsecret":"er9i/53546V3MMu8RfnFuVkVPsChL2bMlfOTQMTPmC6IAJc++Do5qhHFTzngUmk+axlQEGhNnCsr55Kchdf/61caICocHv7Sn9yQy2g0NPPBCFhLIWtlYp9nB6374l4AADNLfdpbrybEYxlWzN/KTwYtqvZcKVvipPfdhBZ2ck7ZJuXJCgU="}

PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
URL = f"{URL_BASE}/{PATH}"

headers = {"Content-Type":"application/json",
           "authorization": f"Bearer {ACCESS_TOKEN}",
           "appKey":APP_KEY,
           "appSecret":APP_SECRET,
           "tr_id":"FHKST01010100"}

params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":"005930"
}

res = requests.get(URL, headers=headers, params=params)
print(res.json()['output']['stck_prpr'])
