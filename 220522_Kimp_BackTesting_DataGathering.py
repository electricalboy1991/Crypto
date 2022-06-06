import pyupbit
import ccxt
import datetime
import pandas as pd

def to_mstimestamp(str):
    str = datetime.datetime.strptime(str, "%Y-%m-%d %H:%M:%S")
    str = datetime.datetime.timestamp(str)
    str = int(str) * 1000
    return str

"""FTX BackTesting Data 가져오기"""
#https://fantagirl.colatribes.com/57

ftx = ccxt.ftx()
start_date = to_mstimestamp('2021-01-01 00:00:00')
# end_date  = to_mstimestamp('2021-12-31 23:59:59')

ohlcv = ftx.fetch_ohlcv('BTC/USDT', timeframe='1h', since=start_date, limit=10000)

ftx_data = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
ftx_data['datetime'] = pd.to_datetime(ftx_data['datetime'], unit='ms') + datetime.timedelta(hours=9)
ftx_data.set_index('datetime', inplace=True)
ftx_data.to_excel("ftx_data.xlsx")

"""Upbit BackTesting Data 가져오기"""
now = datetime.datetime.now()
ticker = 'KRW-BTC'
count_hour = len(ftx_data)
interval_hour = 'minute60'

upbit_data = pyupbit.get_ohlcv(ticker=ticker, to="20210728 07:00:00", interval=interval_hour, count=count_hour)
upbit_data.to_excel("upbit_data.xlsx")

"""환율 엑셀 정보 가져오기"""
USDKRW_data = pd.read_excel("USDKRW.xlsx", engine = "openpyxl")
