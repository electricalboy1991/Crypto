import pyupbit
import pandas as pd
import numpy as np
import datetime
import math

access_key = "mpCGRiTCqlza4eKywK6AIikXQ9ABX3dqQkyuTc3w"
secret_key = "megYxQfiLpuII681da1vlX2bC9EcGXI0iyg6odSQ"
server_url = "https://api.upbit.com"
upbit = pyupbit.Upbit(access_key, secret_key)


'''Variable'''
MA = 24
ticker = 'KRW-BTC'
now = datetime.datetime.now()
count_day = 41
count_hour = 40*24
interval_hour = 'minute60'
balance_manwon = math.trunc(0.0001*float(balance[0]['balance']))
balance_won = float(balance[0]['balance'])

pd.set_option('display.float_format', lambda x: '%.2f' % x)

#한시간에 한번 돌도록 while문 만들어 줘야함.

while(1):

    balance = upbit.get_balances()
    df_day = pyupbit.get_ohlcv(ticker=ticker, to=now, count=count_day)
    df_hour = pyupbit.get_ohlcv(ticker=ticker, to=now, interval=interval_hour, count=count_hour)

    '''day기준 RSI'''
    df_day['변화량'] = df_day['close'] - df_day['close'].shift(1)
    df_day['상승폭'] = np.where(df_day['변화량'] >= 0, df_day['변화량'], 0)
    df_day['하락폭'] = np.where(df_day['변화량'] < 0, df_day['변화량'].abs(), 0)

    df_day['AU'] = df_day['상승폭'].ewm(alpha=1 / 14, min_periods=14).mean()
    df_day['AD'] = df_day['하락폭'].ewm(alpha=1 / 14, min_periods=14).mean()
    # df_day['RS'] = df_day['AU'] / df_day['AD']
    # df_day['RSI'] = 100 - (100 / (1 + df_day['RS']))
    df_day['RSI'] = df_day['AU'] / (df_day['AU'] + df_day['AD']) * 100
    df_day['RSI_MA'] = df_day['RSI'].rolling(MA).mean()

    '''Hour기준 RSI'''
    df_hour['변화량'] = df_hour['close'] - df_hour['close'].shift(1)
    df_hour['상승폭'] = np.where(df_hour['변화량'] >= 0, df_hour['변화량'], 0)
    df_hour['하락폭'] = np.where(df_hour['변화량'] < 0, df_hour['변화량'].abs(), 0)

    df_hour['AU'] = df_hour['상승폭'].ewm(alpha=1 / 14, min_periods=14).mean()
    df_hour['AD'] = df_hour['하락폭'].ewm(alpha=1 / 14, min_periods=14).mean()
    # df_hour['RS'] = df_hour['AU'] / df_hour['AD']
    # df_hour['RSI'] = 100 - (100 / (1 + df_hour['RS']))
    df_hour['RSI'] = df_hour['AU'] / (df_hour['AU'] + df_hour['AD']) * 100

    if balance_manwon == 20:
        if df_day["RSI_MA"][-1] < 50:
            if df_hour["RSI"][-1] < 25.1:
                pyupbit.buy_market_order(ticker, balance_won/1.0005)

    else:
        continue
