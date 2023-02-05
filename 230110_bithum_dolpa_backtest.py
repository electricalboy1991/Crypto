import pyupbit
import time
import matplotlib.pyplot as plt

go_up_period = [['20171220 09:00:00',180],['20190709 09:00:00',180],['20200901 09:00:00',170],['20210220 09:00:00',180],['20211110 09:00:00',120]]
go_down_period = [['20180620 09:00:00',180],['20181220 09:00:00',180],['20200101 09:00:00',140],['20210717 09:00:00',90],['20220701 09:00:00',90]]
stable_period = [['20190330 09:00:00',120],['20200512 09:00:00',110],['20221104 09:00:00',135],['20230109 09:00:00',50]]

go_up_df = []
go_down_df = []
stable_df = []

for i,infor in enumerate(go_up_period):
    temp_data = pyupbit.get_ohlcv(ticker='KRW-BTC',interval='day',count=infor[1],to=infor[0],period=0.1)
    time.sleep(0.1)
    go_up_df.append(temp_data)

for j,infor in enumerate(go_down_period):
    temp_data = pyupbit.get_ohlcv(ticker='KRW-BTC',interval='day',count=infor[1],to=infor[0],period=0.1)
    time.sleep(0.1)
    go_down_df.append(temp_data)

for k,infor in enumerate(stable_period):
    temp_data = pyupbit.get_ohlcv(ticker='KRW-BTC',interval='day',count=infor[1],to=infor[0],period=0.1)
    time.sleep(0.1)
    stable_df.append(temp_data)

def dolpa_go_up(df, k):

    trade_range = (df['high'] - df['low']) * k

    target = df['open'] + trade_range.shift(1)

    criteria = df['high'] >= target
    buy = target[criteria]
    sell = df.loc[criteria, 'close']

    profit_rate = sell / buy

    return profit_rate.cumprod().iloc[-1]

def dolpa_go_down(df, k):

    trade_range = (df['high'] - df['low']) * k

    target = df['open'] - trade_range.shift(1)

    criteria = df['low'] <= target
    short = target[criteria]
    long = df.loc[criteria, 'close']

    profit_rate = 1+(short-long)/ short

    return profit_rate.cumprod().iloc[-1]

data_list = [go_up_df,go_down_df,stable_df]

for tt,kk in enumerate(data_list):
    if tt== 0:
        period = go_up_period
    elif tt == 1:
        period = go_down_period
    else:
        period = stable_period
    for k,i in enumerate(kk):
        print('\n')
        print(period[k][0], "기간 : ", period[k][1])
        for j in range(4,9):
            profit_rate = dolpa_go_up(i,j/10)*dolpa_go_down(i,j/10)
            print(j/10, profit_rate)

        print("\n")


for jj,yy in enumerate(go_up_df):
    yy.plot(title=str(go_up_period[jj][0])+'↗',kind='line',y='close')
    plt.show()

for jj,yy in enumerate(go_down_df):
    yy.plot(title=str(go_down_period[jj][0]+'↘'),kind='line',y='close')
    plt.show()

for jj, yy in enumerate(stable_df):
    yy.plot(title=str(stable_period[jj][0]+'→'), kind='line', y='close')
    plt.show()