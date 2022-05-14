import pyupbit
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

'''Variable'''
MA = 24
ticker = 'KRW-BTC'
now = datetime.datetime.now()
count_day = 365*5+1 #365일 * 5년 + indexing 맞추기 위한 1
count_hour =  365*5*24 #365일 * 5년 * 24 시간
interval_hour = 'minute60'

pd.set_option('display.float_format', lambda x: '%.2f' % x)
df_day = pyupbit.get_ohlcv(ticker=ticker, to=now, count=count_day)
df_hour = pyupbit.get_ohlcv(ticker=ticker, to=now, interval=interval_hour, count=count_hour)

'''day기준 RSI'''
df_day['변화량'] = df_day['close'] - df_day['close'].shift(1)
df_day['상승폭'] = np.where(df_day['변화량']>=0, df_day['변화량'], 0)
df_day['하락폭'] = np.where(df_day['변화량'] <0, df_day['변화량'].abs(), 0)

df_day['AU'] = df_day['상승폭'].ewm(alpha=1/14, min_periods=14).mean()
df_day['AD'] = df_day['하락폭'].ewm(alpha=1/14, min_periods=14).mean()
#df_day['RS'] = df_day['AU'] / df_day['AD']
#df_day['RSI'] = 100 - (100 / (1 + df_day['RS']))
df_day['RSI'] = df_day['AU'] / (df_day['AU'] + df_day['AD']) * 100
df_day['RSI_MA'] = df_day['RSI'].rolling(MA).mean()
df_day[np.isnan(df_day)] = 0

'''Hour기준 RSI'''
df_hour['변화량'] = df_hour['close'] - df_hour['close'].shift(1)
df_hour['상승폭'] = np.where(df_hour['변화량']>=0, df_hour['변화량'], 0)
df_hour['하락폭'] = np.where(df_hour['변화량'] <0, df_hour['변화량'].abs(), 0)

df_hour['AU'] = df_hour['상승폭'].ewm(alpha=1/14, min_periods=14).mean()
df_hour['AD'] = df_hour['하락폭'].ewm(alpha=1/14, min_periods=14).mean()
#df_hour['RS'] = df_hour['AU'] / df_hour['AD']
#df_hour['RSI'] = 100 - (100 / (1 + df_hour['RS']))
df_hour['RSI'] = df_hour['AU'] / (df_hour['AU'] + df_hour['AD']) * 100
df_hour['RSI_MA'] = df_hour['RSI'].rolling(MA).mean()
df_hour[np.isnan(df_hour)] = 0



