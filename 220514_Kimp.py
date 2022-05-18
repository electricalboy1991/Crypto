import ccxt
import pyupbit
import requests
import math
from ftx import FtxClient

client= FtxClient()

upbit_access_key = "mpCGRiTCqlza4eKywK6AIikXQ9ABX3dqQkyuTc3w"
upbit_secret_key = "megYxQfiLpuII681da1vlX2bC9EcGXI0iyg6odSQ"
server_url = "https://api.upbit.com"

upbit = pyupbit.Upbit(upbit_access_key, upbit_secret_key)

def upbit_get_usd_krw():
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange =requests.get(url, headers=headers).json()
    return exchange[0]['basePrice']

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

ftx = ccxt.ftx()
while(1):
    try:

        upbit_price_BTC_current = pyupbit.get_current_price("KRW-BTC")
        ftx_price_BTC = ftx.fetch_ticker("BTC/USDT")
        ftx_price_BTC_current = ftx_price_BTC['close']
        won_rate = upbit_get_usd_krw()
        kimp = (upbit_price_BTC_current / (ftx_price_BTC_current * won_rate) - 1) * 100

        balance = upbit.get_balances()
        balance_manwon = math.trunc(0.0001 * float(balance[0]['balance']))

        # print(upbit_price_BTC_current)
        # print(binance_price_BTC_current*won_rate)
        # print(round(kimp,2))
        if kimp < 1:
            if (kimp < 1 and kimp > 0):
                if balance_manwon == 100:
                    print("처음 산다")
                else:
                    continue
            else:  # 김프가 0 이하
                if balance_manwon == 50:
                    print("더사서 평단 낮춘다.")
                else:
                    continue
        if kimp > 3:
            print("판다")

    except:
        print("Error")