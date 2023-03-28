#-*-coding:utf-8 -*-
import myBinance_USDT   #우리가 만든 함수들이 들어있는 모듈
import time
import ccxt
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키
import line_alert
import json
import platform
from datetime import datetime
import numpy as np
from pytz import timezone

if platform.system() == 'Windows':
    pass
else:
    time.sleep(5)

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance_USDT.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)

##미국 0시 기준으로 몇시간 뒤를 청산 시간으로 잡을지임
hour_shift = 9

#청산 기준 시간,
hour_crit = 23
min_crit = 54

#시간 정보를 가져옵니다. 아침 9시의 경우 서버에서는 hour변수가 0이 됩니다. 범위 [0, 6], 월요일은 0
time_info = time.gmtime()
hour_usa = time_info.tm_hour
#여기서 hour는 내가 청산 기준으로 잡은 시간에서 몇 시간이 지났냐임
hour = time_info.tm_hour-hour_shift
if hour <0:
    hour = hour+24
minute = time_info.tm_min
month = time_info.tm_mon
day = time_info.tm_mday
wday = time_info.tm_wday

print(hour, minute)

#내가 매수할 총 코인 개수
MaxCoinCnt = 10
k_parameter = 0.39
k_parameter_2 = 0.59
GetInMoney = 50
variability_range = 0.02
set_leverage=3
average_noise = 0.58
commission_rate = 0.002
sum_PNL = 0
sum_isolated_cost = 0
num_BV_ing_ticker = 0
#short투입시에는 long투입과 비교 시, 손실이 길게 가끔나는 편이라, 손실을 좀 길게 가져가도...
short_stoploss_ratio = 1.1
loss_cut_ratio = 0.03
rsi_crit_bottom_BTC = 19
rsi_crit_top_BTC = 100 - rsi_crit_bottom_BTC
rsi_crit_bottom_ticker = 8
rsi_crit_top_ticker = 100 - rsi_crit_bottom_ticker

rsi_hour_filter_upper = 70
rsi_hour_filter_lower = 100-rsi_hour_filter_upper

rsi_BTC_ticker = 'BTC/USDT'
MA_cut_num = 7
revenue_rate_cut = 0.01
one_minute_offset = 0.008
loss_cut_range_ratio = 1.5
#5일치 rsi_hour를 보겠다는 거임, 진입을 오랫동안 거래량 안터진 방향으로 진행하기 위함
hour_rsi_length = 100

Telegram_Log = dict()

##############################################################
#수익율 0.5%를 트레일링 스탑 기준으로 잡는다. 즉 고점 대비 0.5% 하락하면 매도 처리 한다!
stop_revenue = 0.15
trailing_stop_ratio = 0.3
##############################################################

if month ==11 or  month ==12 or  month ==1 or  month ==2 or  month ==3 or  month ==4:
    season_weight_long = 1.1
    season_weight_short = 1.0
else:
    season_weight_long = 1.0
    season_weight_short = 1.1

time.sleep(0.05)

# binance 객체 생성
binanceX = ccxt.binance(config={'apiKey': Binance_AccessKey,'secret': Binance_ScretKey,'enableRateLimit': True,'options': {'defaultType': 'future'}})

#잔고 데이타 가져오기
balance_binance = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)

#코인당 매수할 매수금액
CoinMoney = balance_binance['USDT']['free'] / MaxCoinCnt

#5천원 이하면 매수가 아예 안되나 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
if CoinMoney < 100:
    CoinMoney = 100

print("-----------------------------------------------")
print ("Total $:", balance_binance['USDT']['free'])
print ("CoinMoney:", CoinMoney)

#파일 경로입니다.
if platform.system() == 'Windows':
    BV_file_path = "C:\\Users\world\PycharmProjects\Crypto\Binance_BV_coin.json"
    BV_top_file_path = "C:\\Users\world\PycharmProjects\Crypto\BV_TopCoinList.json"
    revenue_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Binance_BV_revenue.json"
    BV_daily_month_profit_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\BV_daily_month_profit.json"
    BV_pole_point_file_path = "C:\\Users\world\PycharmProjects\Crypto\BV_pole_point.json"
    BV_noise_median_file_path = "C:\\Users\world\PycharmProjects\Crypto\BV_noise_median.json"
    BV_cnt_file_path = "C:\\Users\world\PycharmProjects\Crypto\BV_cnt.json"
else:
    BV_file_path = "/var/autobot/Binance_BV_coin.json"
    BV_top_file_path = "/var/autobot/BV_TopCoinList.json"
    revenue_type_file_path = "/var/autobot/Binance_BV_revenue.json"
    BV_daily_month_profit_type_file_path = "/var/autobot/BV_daily_month_profit.json"
    BV_pole_point_file_path = "/var/autobot/BV_pole_point.json"
    BV_noise_median_file_path = "/var/autobot/BV_noise_median.json"
    BV_cnt_file_path = "/var/autobot/BV_cnt.json"

BV_cnt = dict()
try:
    #이 부분이 파일을 읽어서 딕셔너리에 넣어주는 로직입니다.
    with open(BV_cnt_file_path, 'r') as json_file:
        if hour == hour_crit and minute == min_crit+2:
            BV_cnt = dict()
            with open(BV_cnt_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(BV_cnt, outfile)
        else:
            BV_cnt = json.load(json_file)
except Exception as e:
    print("BV_cnt Exception by First")

BV_coinlist = list()
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(BV_file_path, 'r') as json_file:
        if hour == hour_crit and minute == min_crit+2:
            BV_coinlist = list()
            with open(BV_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(BV_coinlist, outfile)
        else:
            BV_coinlist = json.load(json_file)

except Exception as e:
    print("BV_coinlist Exception by First")

TopCoinList = list()
#파일을 읽어서 리스트를 만듭니다.
try:
    with open(BV_top_file_path, "r") as json_file:
        TopCoinList = json.load(json_file)
        #이거 quarter 날짜 들어가있는 Coin때문에, 아래에서 median 생성이 안되는 오류 있었음. 그거 때문에 추가.
        TopCoinList = [s for s in TopCoinList if len(s) <= 18]
        if hour == hour_crit and minute == min_crit+2 and len(BV_coinlist) == 0:
            TopCoinList = myBinance_USDT.GetTopCoinList(binanceX, 50)
            with open(BV_top_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(TopCoinList, outfile)

except Exception as e:
    TopCoinList = myBinance_USDT.GetTopCoinList(binanceX,20)
    print("TopCoinList Exception by First")
    with open(BV_top_file_path, 'w', encoding="utf-8") as outfile:
        json.dump(TopCoinList, outfile)

BV_revenue_dict = dict()
try:
    #이 부분이 파일을 읽어서 딕셔너리에 넣어주는 로직입니다.
    with open(revenue_type_file_path, 'r') as json_file:
        if hour == hour_crit and minute == min_crit+2:
            BV_revenue_dict = dict()
            with open(revenue_type_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(BV_revenue_dict, outfile)
        else:
            BV_revenue_dict = json.load(json_file)
except Exception as e:
    print("BV_revenue_dict Exception by First")


BV_pole_point_dict = dict()
try:
    #이 부분이 파일을 읽어서 딕셔너리에 넣어주는 로직입니다.
    with open(BV_pole_point_file_path, 'r') as json_file:
        if hour == hour_crit and minute == min_crit+2:
            BV_pole_point_dict = dict()
            with open(BV_pole_point_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(BV_pole_point_dict, outfile)
        else:
            BV_pole_point_dict = json.load(json_file)
except Exception as e:
    print("BV_pole_point_dict Exception by First")

BV_daily_month_profit = {"month" : 0, "daily" : 0,"day_based_win" : 0,"day_based_lose" : 0,
                         "totol_profit_ratio" : 0,"cumulative_win_dollor" : 0,"cumulative_lose_dollor" : 0}
for jjj in TopCoinList:
    #각 코인별 승,패,누적 승$,누적 패$, 손익비
    BV_daily_month_profit[jjj] =[1,1,1,-1,0]

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(BV_daily_month_profit_type_file_path, 'r', encoding="utf-8") as json_file:
        if hour == hour_crit and minute == min_crit + 2:
            BV_daily_month_profit = json.load(json_file)
            BV_daily_month_profit["daily"] = 0
            if day ==1 and hour==hour_crit and minute == min_crit + 2:
                BV_daily_month_profit["month"] = 0

            with open(BV_daily_month_profit_type_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(BV_daily_month_profit, outfile)
        else:
            BV_daily_month_profit = json.load(json_file)
except Exception as e:
    print("BV_daily_month_profit Exception by First 0")

#노이즈에 따라서 coin 걸러 내려고 했는데, 수익률이 높은 코인들이 걸러지는 것 같아서 일단 보류

temp_TopCoinList = []
remove_list = []
for tt in TopCoinList:
    temp_ticker=tt.replace(":USDT", "")
    temp_TopCoinList.append(temp_ticker)

TopCoinList=temp_TopCoinList
if not remove_list:
    pass
else:
    for i in remove_list:
        TopCoinList.remove(i)

noise_median_dict = dict()
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(BV_noise_median_file_path, 'r', encoding="utf-8") as json_file:
        if hour == hour_crit and minute == min_crit + 2:
            noise_median_dict = json.load(json_file)
            for ticker in TopCoinList:
                df_day = myBinance_USDT.GetOhlcv(binanceX, ticker, '1d')
                df_day_for_noise = df_day[:][-365:]
                df_day_for_noise['noise'] = noise_now = 1 - abs((df_day_for_noise['open'] - df_day_for_noise['close']) / (df_day_for_noise['high'] - df_day_for_noise['low']))
                noise_median_dict[ticker] = df_day_for_noise['noise'].median()

            with open(BV_noise_median_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(noise_median_dict, outfile)
        else:
            noise_median_dict = json.load(json_file)
except Exception as e:
    print("BV_noise_median_dict Exception by First 0")

#한국시간 9시 -> 0

#거래대금 탑 코인 리스트를 1위부터 내려가며 매수 대상을 찾는다.
#전체 마켓의 코인이 아니라 탑 순위 TopCoinList 안에 있는 코인만 체크해서 매수

#"""

df_rsi_BTC = myBinance_USDT.GetOhlcv(binanceX, rsi_BTC_ticker, '1h')
rsi_hour_BTC = float(myBinance_USDT.GetRSI(df_rsi_BTC, 14, -1))
rsi_hour_list = []
for ttt in range(hour_rsi_length):
    rsi_hour_list.append(float(myBinance_USDT.GetRSI(df_rsi_BTC, 14, -ttt)))


if hour ==hour_crit and (minute ==min_crit or minute ==min_crit+1  or minute ==min_crit+2  or minute ==min_crit+3  or minute ==min_crit+4  or minute ==min_crit+5 ):
    pass
# elif (wday ==5 and 9 <= hour_usa <= 23) or (wday ==0 and 0 <= hour_usa <= 8) or wday ==6 :
#     pass
else:
    for ticker in TopCoinList[0:10]:
        try:
            print("Coin Ticker: ",ticker)
            Target_Coin_Symbol = ticker.replace("/", "")

            #포지션 유무를 미리 알기 위한 코드
            Target_Coin_Symbol_index = 0
            amt = 0
            for posi in balance_binance['info']['positions']:
                if Target_Coin_Symbol_index == 2:
                    break
                if posi['symbol'] == Target_Coin_Symbol:
                    Target_Coin_Symbol_index=Target_Coin_Symbol_index+1
                    if float(posi['positionAmt']) != 0:
                        entryPrice = float(posi['entryPrice'])
                        if float(posi['positionAmt']) < 0:
                            amt = float(posi['positionAmt'])
                            leverage = float(posi['leverage'])
                            isolated = posi['isolated']
                            break
                        elif float(posi['positionAmt']) > 0:
                            amt = float(posi['positionAmt'])
                            leverage = float(posi['leverage'])
                            isolated = posi['isolated']
                            break

            time.sleep(0.05)
            df = myBinance_USDT.GetOhlcv(binanceX, ticker, '1h')  # 일봉 데이타를 가져온다.

            BV_range = (float(max(df['high'][-(hour + 25):-(hour + 1)])) - float(min(df['low'][-(hour + 25):-(hour + 1)]))) * k_parameter
            BV_range_2 = (float(max(df['high'][-(hour + 25):-(hour + 1)])) - float(min(df['low'][-(hour + 25):-(hour + 1)]))) * k_parameter_2
            now_price = float(df['close'][-1])

            df_rsi_BTC = myBinance_USDT.GetOhlcv(binanceX, rsi_BTC_ticker, '1h')
            rsi_hour_BTC = float(myBinance_USDT.GetRSI(df_rsi_BTC, 14, -1))

            # df_rsi_ticker = myBinance_USDT.GetOhlcv(binanceX, ticker, '1h')
            # rsi_hour_ticker = float(myBinance_USDT.GetRSI(df_rsi_ticker, 14, -1))
            # rsi_hour_list = []
            # for ttt in range(hour_rsi_length):
            #     rsi_hour_list.append(float(myBinance_USDT.GetRSI(df_rsi_ticker, 14, -ttt)))

            time.sleep(0.05)
            # 하루 동안 산적이 없는 애다
            if not (ticker in BV_cnt):

                up_target = float(df['open'][-(hour+1)]) + BV_range
                down_target = float(df['open'][-(hour+1)]) - BV_range

                df_day = myBinance_USDT.GetOhlcv(binanceX, ticker, '1d')

                range_rate=(float(max(df['high'][-(hour + 25):-(hour + 1)])) - float(min(df['low'][-(hour + 25):-(hour + 1)]))) / float(df['open'][-(hour + 1)])

                # 거래량 계산 구간
                volume_average = float(np.sum(df['volume'][-72:])/3)
                volume_now = float(np.sum(df['volume'][-24:]))
                if wday ==5 or wday==6:
                    volume_average = volume_now

                print("현재가 : ",now_price , "상승 타겟 : ", up_target, "하락 타겟 : ", down_target)
                time.sleep(0.05)
                #이를 돌파했다면 변동성 돌파 성공!! 코인을 매수하고 지정가 익절을 걸고 파일에 해당 코인을 저장한다!
                if now_price > up_target and len(BV_coinlist) < MaxCoinCnt and hour !=hour_crit and not any(num > rsi_hour_filter_upper for num in rsi_hour_list):
                # if now_price > up_target and len(BV_coinlist) < MaxCoinCnt and now_price >= max(df['high'][-(hour + 1):]) and hour != hour_crit and rsi_hour_BTC < rsi_crit_top_BTC \
                #         and rsi_hour_ticker < rsi_crit_top_ticker:  # and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt:
                #if now_price > up_target and len(BV_coinlist) < MaxCoinCnt:  # and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt:
                    for posi in balance_binance['info']['positions']:
                        if posi['symbol'] == Target_Coin_Symbol:
                            back_2_ticker = False

                            #사는 구간
                            if float(posi['positionAmt']) ==0:
                                leverage = float(posi['leverage'])
                                isolated = posi['isolated']
                                break
                            else:
                                #다음 ticker로 넘어가는 구간
                                back_2_ticker = True
                                break

                    if back_2_ticker ==True:
                        continue

                    print("!!!!!!!!!!!!!!!BV go up!!!!!!!!!!!!!!!!!!!!!!!!")

                    #노이즈 계산 구간
                    noise_range_max = float(max(df['high'][-24:]))
                    noise_range_min = float(min(df['low'][-24:]))
                    noise_range_open = float(df['open'][-24])
                    noise_now = 1-abs((now_price-noise_range_open)/(noise_range_max-noise_range_min))

                    minimun_amount = myBinance_USDT.GetMinimumAmount(binanceX, ticker)
                    Buy_Amt = float(binanceX.amount_to_precision(ticker, (volume_now/volume_average)*season_weight_long*(noise_median_dict[ticker]/noise_now)*(variability_range/range_rate)*(GetInMoney / now_price) * set_leverage))
                    Buy_Amt_limit = float(binanceX.amount_to_precision(ticker, (GetInMoney / now_price) * set_leverage))

                    if Buy_Amt>=Buy_Amt_limit:
                        Buy_Amt = Buy_Amt_limit
                    # 최소 주문 수량보다 작다면 이렇게 셋팅!
                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    #################################################################################################################
                    # 레버리지 셋팅
                    if leverage != set_leverage:

                        try:
                            print(binanceX.fapiPrivate_post_leverage(
                                {'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                        except Exception as e:
                            print("Exception:", e)

                    # 격리 모드로 설정
                    if isolated == False:
                        try:
                            print(binanceX.fapiPrivate_post_margintype(
                                {'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
                        except Exception as e:
                            print("Exception:", e)
                    #################################################################################################################

                    #시장가 매수를 한다.

                    params = {'positionSide': 'LONG'}
                    print(binanceX.create_order(ticker, 'market', 'buy', Buy_Amt, None, params))
                    time.sleep(0.05)
                    #매수된 코인을 BV_coinlist 리스트에 넣고 이를 파일로 저장해둔다!
                    BV_coinlist.append(ticker)

                    #파일에 리스트를 저장합니다
                    with open(BV_file_path, 'w') as outfile:
                        json.dump(BV_coinlist, outfile)

                    #매수와 동시에 초기 수익율을 넣는다. (당연히 0일테니 0을 넣고)
                    BV_revenue_dict[ticker] = 0

                    #파일에 딕셔너리를 저장합니다
                    with open(revenue_type_file_path, 'w') as outfile:
                        json.dump(BV_revenue_dict, outfile)

                    # 매수와 동시에 초기 값을 넣는다.
                    BV_pole_point_dict[ticker] = now_price
                    # 파일에 딕셔너리를 저장합니다
                    with open(BV_pole_point_file_path, 'w') as outfile:
                        json.dump(BV_pole_point_dict, outfile)

                    BV_cnt[ticker] = 1
                    with open(BV_cnt_file_path, 'w') as outfile:
                        json.dump(BV_cnt, outfile)

                    balance_binance = binanceX.fetch_balance(params={"type": "future"})
                    isolated_cost = 0
                    for posi in balance_binance['info']['positions']:
                        if posi['symbol'] == Target_Coin_Symbol and float(posi['positionAmt']) != 0:
                            # 사는 구간
                            isolated_cost = float(posi['isolatedWallet'])

                    #이렇게 매수했다고 메세지를 보낼수도 있다
                    line_alert.SendMessage_SP("[\U0001F4C8Long BV] : " + ticker + " 진입 cnt : " +str(BV_cnt[ticker]) + "\n현재 가격 : " + str(round(now_price, 4))+"$\n투입액 : " + str(round(isolated_cost, 4))+ "$")

                elif now_price < down_target and len(BV_coinlist) < MaxCoinCnt and hour !=hour_crit and not any(num < rsi_hour_filter_lower for num in rsi_hour_list):
                # elif now_price < down_target and len(BV_coinlist) < MaxCoinCnt and now_price <= min(df['low'][-(hour + 1):]) and hour != hour_crit \
                #         and rsi_hour_BTC > rsi_crit_bottom_BTC and rsi_hour_ticker > rsi_crit_bottom_ticker:
                #elif now_price < down_target and len(BV_coinlist) < MaxCoinCnt:
                    for posi in balance_binance['info']['positions']:
                        if posi['symbol'] == Target_Coin_Symbol:
                            back_2_ticker = False

                            # 사는 구간
                            if float(posi['positionAmt']) == 0:
                                leverage = float(posi['leverage'])
                                isolated = posi['isolated']
                                break

                            # 이미 포지션 잡고 있는 코인이기 때문에, 다음 티커로 넘어가는 코드 -> for문으로 보내라
                            else:
                                # 다음 ticker로 넘어가는 구간
                                back_2_ticker = True
                                break

                    if back_2_ticker == True:
                        continue
                    print("!!!!!!!!!!!!!!!BV go down!!!!!!!!!!!!!!!!!!!!!!!!")

                    # 노이즈 계산 구간
                    noise_range_max = float(max(df['high'][-24:]))
                    noise_range_min = float(min(df['low'][-24:]))
                    noise_range_open = float(df['open'][-24])
                    noise_now = 1 - abs((now_price - noise_range_open) / (noise_range_max - noise_range_min))

                    minimun_amount = myBinance_USDT.GetMinimumAmount(binanceX, ticker)
                    Buy_Amt = float(binanceX.amount_to_precision(ticker, (volume_now/volume_average)*season_weight_short*(noise_median_dict[ticker]/noise_now)*(variability_range/range_rate)*(GetInMoney / now_price) * set_leverage))

                    Buy_Amt_limit = float(binanceX.amount_to_precision(ticker, (GetInMoney / now_price) * set_leverage))

                    if Buy_Amt >= Buy_Amt_limit:
                        Buy_Amt = Buy_Amt_limit

                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    #################################################################################################################
                    # 레버리지 셋팅
                    if leverage != set_leverage:

                        try:
                            print(binanceX.fapiPrivate_post_leverage(
                                {'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                        except Exception as e:
                            print("Exception:", e)

                    # 격리 모드로 설정
                    if isolated == False:
                        try:
                            print(binanceX.fapiPrivate_post_margintype(
                                {'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
                        except Exception as e:
                            print("Exception:", e)
                    #################################################################################################################

                    params = {'positionSide': 'SHORT'}
                    print(binanceX.create_order(ticker, 'market', 'sell', Buy_Amt, None, params))
                    time.sleep(0.05)
                    # 매수된 코인을 BV_coinlist 리스트에 넣고 이를 파일로 저장해둔다!
                    BV_coinlist.append(ticker)

                    # 파일에 리스트를 저장합니다
                    with open(BV_file_path, 'w') as outfile:
                        json.dump(BV_coinlist, outfile)

                    # 매수와 동시에 초기 수익율을 넣는다. (당연히 0일테니 0을 넣고)
                    BV_revenue_dict[ticker] = 0

                    # 파일에 딕셔너리를 저장합니다
                    with open(revenue_type_file_path, 'w') as outfile:
                        json.dump(BV_revenue_dict, outfile)

                    # 매수와 동시에 초기 값을 넣는다.
                    BV_pole_point_dict[ticker] = now_price
                    # 파일에 딕셔너리를 저장합니다
                    with open(BV_pole_point_file_path, 'w') as outfile:
                        json.dump(BV_pole_point_dict, outfile)

                    BV_cnt[ticker] = -1
                    with open(BV_cnt_file_path, 'w') as outfile:
                        json.dump(BV_cnt, outfile)

                    isolated_cost = 0
                    balance_binance = binanceX.fetch_balance(params={"type": "future"})
                    for posi in balance_binance['info']['positions']:
                        if posi['symbol'] == Target_Coin_Symbol and float(posi['positionAmt']) != 0:
                            # 사는 구간
                            isolated_cost = float(posi['isolatedWallet'])

                    # 이렇게 매수했다고 메세지를 보낼수도 있다
                    line_alert.SendMessage_SP("[\U0001F4C9Short BV] : " + ticker +" 진입 cnt : " +str(BV_cnt[ticker]) + "\n현재 가격 : " + str(round(now_price, 4))+"$\n투입액 : " + str(round(isolated_cost, 4))+ "$")

            # 롱 불 타기 1회
            elif amt >0 and now_price > float(df['open'][-(hour+1)]) + BV_range_2 and BV_cnt[ticker]==1:
            # elif amt > 0 and now_price > entryPrice + BV_range_2 and BV_cnt[ticker] == 1 and rsi_hour_BTC < rsi_crit_top_BTC and rsi_hour_ticker < rsi_crit_top_ticker:

                minimun_amount = myBinance_USDT.GetMinimumAmount(binanceX, ticker)
                Buy_Amt = float(binanceX.amount_to_precision(ticker, float(abs(amt))*2/3))

                if Buy_Amt < minimun_amount:
                    Buy_Amt = minimun_amount
                #################################################################################################################
                # 레버리지 셋팅
                if leverage != set_leverage:

                    try:
                        print(binanceX.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                    except Exception as e:
                        print("Exception:", e)

                # 격리 모드로 설정
                if isolated == False:
                    try:
                        print(binanceX.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
                    except Exception as e:
                        print("Exception:", e)
                #################################################################################################################

                # 시장가 매수를 한다.
                params = {'positionSide': 'LONG'}
                print(binanceX.create_order(ticker, 'market', 'buy', Buy_Amt, None, params))
                time.sleep(0.05)
                # 매수와 동시에 수익률
                PNL = 0
                isolated_cost = 0
                balance_binance = binanceX.fetch_balance(params={"type": "future"})
                for posi in balance_binance['info']['positions']:
                    if posi['symbol'] == Target_Coin_Symbol and float(posi['positionAmt']) != 0:
                        # 사는 구간
                        PNL = float(posi['unrealizedProfit'])
                        isolated_cost = float(posi['isolatedWallet'])

                BV_revenue_dict[ticker] = PNL/isolated_cost

                # 파일에 딕셔너리를 저장합니다
                with open(revenue_type_file_path, 'w') as outfile:
                    json.dump(BV_revenue_dict, outfile)

                # 매수와 동시에 초기 값을 넣는다.
                BV_pole_point_dict[ticker] = now_price
                # 파일에 딕셔너리를 저장합니다
                with open(BV_pole_point_file_path, 'w') as outfile:
                    json.dump(BV_pole_point_dict, outfile)

                # cnt 2의 의미는 진입했다가 -> 이미 불 탔다
                BV_cnt[ticker] = 2
                with open(BV_cnt_file_path, 'w') as outfile:
                    json.dump(BV_cnt, outfile)

                # 이렇게 매수했다고 메세지를 보낼수도 있다
                line_alert.SendMessage_SP("[\U0001F4C8 \U0001F525 Long BV] : " + ticker +" 진입 cnt : " +str(BV_cnt[ticker]) +"\n현재 가격 : " + str(round(now_price, 4)) +"$\n투입액 : " + str(round(isolated_cost, 4)) + "$")
                pass

            #숏 불타기 1회
            elif amt <0 and now_price < float(df['open'][-(hour+1)]) - BV_range_2 and BV_cnt[ticker]==-1:
            # elif amt < 0 and now_price < entryPrice - BV_range_2 and BV_cnt[ticker] == -1 and rsi_hour_BTC > rsi_crit_bottom_BTC and rsi_hour_ticker > rsi_crit_bottom_ticker:

                minimun_amount = myBinance_USDT.GetMinimumAmount(binanceX, ticker)
                Buy_Amt = float(binanceX.amount_to_precision(ticker, float(abs(amt))*2/3))

                if Buy_Amt < minimun_amount:
                    Buy_Amt = minimun_amount
                #################################################################################################################
                # 레버리지 셋팅
                if leverage != set_leverage:

                    try:
                        print(binanceX.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                    except Exception as e:
                        print("Exception:", e)

                # 격리 모드로 설정
                if isolated == False:
                    try:
                        print(binanceX.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
                    except Exception as e:
                        print("Exception:", e)
                #################################################################################################################

                # 시장가 매수를 한다.
                params = {'positionSide': 'SHORT'}
                print(binanceX.create_order(ticker, 'market', 'sell', Buy_Amt, None, params))
                time.sleep(0.05)
                # 매수와 동시에 수익률
                PNL = 0
                isolated_cost = 0
                balance_binance = binanceX.fetch_balance(params={"type": "future"})
                for posi in balance_binance['info']['positions']:
                    if posi['symbol'] == Target_Coin_Symbol and float(posi['positionAmt']) != 0:
                        # 사는 구간
                        PNL = float(posi['unrealizedProfit'])
                        isolated_cost = float(posi['isolatedWallet'])

                BV_revenue_dict[ticker] = PNL / isolated_cost

                # 파일에 딕셔너리를 저장합니다
                with open(revenue_type_file_path, 'w') as outfile:
                    json.dump(BV_revenue_dict, outfile)

                # 매수와 동시에 초기 값을 넣는다.
                BV_pole_point_dict[ticker] = now_price
                # 파일에 딕셔너리를 저장합니다
                with open(BV_pole_point_file_path, 'w') as outfile:
                    json.dump(BV_pole_point_dict, outfile)

                # cnt 2의 의미는 진입했다가 -> 이미 불 탔다
                BV_cnt[ticker] = -2
                with open(BV_cnt_file_path, 'w') as outfile:
                    json.dump(BV_cnt, outfile)

                # 이렇게 매수했다고 메세지를 보낼수도 있다
                line_alert.SendMessage_SP("[\U0001F4C9 \U0001F525 Short BV] : " + ticker +" 진입 cnt : " +str(BV_cnt[ticker]) + "\n현재 가격 : " + str(round(now_price, 4)) + "$\n투입액 : " + str(round(isolated_cost, 4)) + "$")

                pass
            else:
                pass
        except Exception as e:
            print("---:", e)
#"""

# 바이낸스 기준 모든 코인을 순회하여 체크한다!
# 이렇게 두번에 걸쳐서 for문을 도는 이유는
# 매수된 코인이 거래대금 탑순위에 (TopCoinList) 빠져서 아예 체크되지 않은 걸 방지하고자
# 매수 후 체크하는 로직은 전체 코인 대상으로 체크하고
# 매수 할때는 TopCoinList안의 코인만 체크해서 매수 합니다.

# if (wday ==5 and 9 <= hour_usa <= 23) or (wday ==0 and 0 <= hour_usa <= 8) or wday ==6 :
#     pass
# else:

off_ticker_list = myBinance_USDT.GetTopCoinList(binanceX,50)

for ticker in off_ticker_list:
    BV_range_index = 0
    loss_cut_index = 0
    BTC_rsi_index = 0
    ticker_rsi_index = 0
    MA_profit_index = 0
    if ":" in ticker:
        ticker = ticker.replace(":USDT", "")
    try:
        print("Condition checked coin ticker: ",ticker)
        Target_Coin_Symbol = ticker.replace("/", "")
        #변동성 돌파로 매수된 코인이다!!! (실제로 매도가 되서 잔고가 없어도 파일에 쓰여있다면 참이니깐 이 안의 로직을 타게 됨)
        if myBinance_USDT.CheckCoinInList(BV_coinlist,ticker) == True:
            # 매수한 상태에서의 수익률을 계산하기 위함임
            print("2")
            amt = 0
            revenue_rate = 0
            PNL = 0
            isolated_cost = 0
            for posi in balance_binance['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol and float(posi['positionAmt']) != 0:
                    # 사는 구간
                    PNL = float(posi['unrealizedProfit'])
                    isolated_cost = float(posi['isolatedWallet'])
                    if float(posi['positionAmt']) != 0:
                        now_price = myBinance_USDT.GetCoinNowPrice(binanceX, ticker)
                        if float(posi['positionAmt']) < 0:
                            amt = float(posi['positionAmt'])
                            revenue_rate = ((PNL) / (isolated_cost*set_leverage))
                            break
                        elif float(posi['positionAmt']) > 0:
                            amt = float(posi['positionAmt'])
                            revenue_rate = ((PNL) / (isolated_cost*set_leverage))
                            break

            sum_PNL = sum_PNL + PNL
            sum_isolated_cost = sum_isolated_cost + isolated_cost

            if amt == 0:
                status = 'Done'
            elif amt > 0:
                status = 'Long'
                num_BV_ing_ticker = num_BV_ing_ticker + 1
            else:
                status = 'Short'
                num_BV_ing_ticker = num_BV_ing_ticker + 1

            Telegram_Log[ticker] = [status, round(revenue_rate, 4), round(PNL, 4), round(isolated_cost, 4)]

            #청산 시간
            if hour == hour_crit and minute == min_crit:

                #매수한 코인이라면.
                for posi in balance_binance['info']['positions']:
                    if posi['symbol'] == Target_Coin_Symbol:
                        # 사는 구간
                        if float(posi['positionAmt']) != 0:
                            amt = float(posi['positionAmt'])
                            #시장가로 모두 매도!
                            if float(posi['positionAmt']) < 0:
                                params = {'positionSide': 'SHORT'}
                                print(binanceX.create_order(ticker, 'market', 'buy', abs(amt), None, params))
                            elif float(posi['positionAmt']) > 0:
                                params = {'positionSide': 'LONG'}
                                print(binanceX.create_order(ticker, 'market', 'sell', abs(amt), None, params))

                #T/S 으로 손절한 경우 바로 리스트에서 제거하지 않고, 청산 기준 시간에 다같이 제거
                #리스트에서 코인을 빼 버린다.
                BV_coinlist.remove(ticker)

                #파일에 리스트를 저장합니다
                with open(BV_file_path, 'w') as outfile:
                    json.dump(BV_coinlist, outfile)

                # 일 확정 수익에 넣어 주는 거임
                # BV_daily_month_profit["daily"] = BV_daily_month_profit["daily"] + PNL
                # BV_daily_month_profit["month"] = BV_daily_month_profit["month"] + PNL

                # 빼주는 이유는 밑에 sum_PNL = sum_PNL + BV_daily_month_profit["daily"] 이거 구할 때, 이미 daily 값에 반영이 되어 있으니까 빼줌
                # sum_PNL = sum_PNL - PNL

                # 코인별 승,패,승 누적 달러, 패 누적 달러, 손익비 저장
                if PNL > 0:
                    BV_daily_month_profit[ticker][0] = BV_daily_month_profit[ticker][0] + 1
                    BV_daily_month_profit[ticker][2] = BV_daily_month_profit[ticker][2] + PNL
                    BV_daily_month_profit[ticker][4] = -BV_daily_month_profit[ticker][2] / BV_daily_month_profit[ticker][3]
                elif PNL < 0:
                    BV_daily_month_profit[ticker][1] = BV_daily_month_profit[ticker][1] + 1
                    BV_daily_month_profit[ticker][3] = BV_daily_month_profit[ticker][3] + PNL
                    BV_daily_month_profit[ticker][4] = -BV_daily_month_profit[ticker][2] / BV_daily_month_profit[ticker][3]

                # 파일에 딕셔너리를 저장합니다
                BV_daily_month_profit["daily"] = BV_daily_month_profit["daily"] + PNL
                BV_daily_month_profit["month"] = BV_daily_month_profit["month"] + PNL
                with open(BV_daily_month_profit_type_file_path, 'w') as outfile:
                    json.dump(BV_daily_month_profit, outfile)

                sum_PNL = 0
            ############################트레일링 스탑 구현을 위한 부분..###################################
            # 수익률 기준이 아닌 변동성 range로 트레일링 스탑 구현

            df_rsi_BTC = myBinance_USDT.GetOhlcv(binanceX, rsi_BTC_ticker, '1h')
            rsi_hour_BTC = float(myBinance_USDT.GetRSI(df_rsi_BTC, 14, -1))

            df_rsi_ticker = myBinance_USDT.GetOhlcv(binanceX, ticker, '1h')
            rsi_hour_ticker = float(myBinance_USDT.GetRSI(df_rsi_ticker, 14, -1))

            df_MA_ticker = myBinance_USDT.GetOhlcv(binanceX, ticker, '1m')
            MA_1m_ticker = myBinance_USDT.GetMA(df_MA_ticker, 14, -1)

            if amt < 0:
                if now_price <= BV_pole_point_dict[ticker] and status != 'Done':
                # if now_price <= BV_pole_point_dict[ticker] and status != 'Done' and rsi_hour_BTC > rsi_crit_bottom_BTC and rsi_hour_ticker > rsi_crit_bottom_ticker:

                    #이렇게 딕셔너리에 값을 넣어주면 된다.
                    BV_pole_point_dict[ticker] = now_price

                    #파일에 딕셔너리를 저장합니다
                    with open(BV_pole_point_file_path, 'w') as outfile:
                        json.dump(BV_pole_point_dict, outfile)

                elif status == 'Done':
                    pass

                else:
                    df = myBinance_USDT.GetOhlcv(binanceX, ticker, '1h')  # 일봉 데이타를 가져온다.
                    BV_range = (float(max(df['high'][-(hour + 25):-(hour + 1)])) - float(min(df['low'][-(hour + 25):-(hour + 1)]))) * k_parameter
                    #short 청산 로직
                    # 손절 로직 : 자산*(받아들일수있는 손실/투자 코인수)*(코인당 투자 액/자산)*코인수 // 반대로 변동성 만큼 떨어지거나, 투자 금액의 2% 손해 이상 보거나, BTC RSI로 청산하거나, 개별코인 RSI로 청산하거나, 1%이상 이익 봤는데, 진입 코인이 7개 이하고, MA 꺾였을 때
                    if PNL<-loss_cut_ratio*GetInMoney*set_leverage or rsi_hour_ticker <= rsi_crit_bottom_ticker :
                    # if now_price - BV_pole_point_dict[ticker] > BV_range * loss_cut_range_ratio or PNL < -loss_cut_ratio * GetInMoney * set_leverage or rsi_hour_ticker <= rsi_crit_bottom_ticker:
                    # if now_price - BV_pole_point_dict[ticker] > BV_range or PNL < -loss_cut_ratio * GetInMoney * set_leverage or rsi_hour_BTC <= rsi_crit_bottom_BTC \
                    #         or rsi_hour_ticker <= rsi_crit_bottom_ticker or (len(BV_coinlist) <= MA_cut_num and now_price > MA_1m_ticker and revenue_rate > revenue_rate_cut):
                        #시장가로 모두 매도!
                        if float(posi['positionAmt']) < 0:
                            params = {'positionSide': 'SHORT'}
                            print(binanceX.create_order(ticker, 'market', 'buy', abs(amt), None, params))
                        elif float(posi['positionAmt']) > 0:
                            params = {'positionSide': 'LONG'}
                            print(binanceX.create_order(ticker, 'market', 'sell', abs(amt), None, params))

                        #빼주는 이유는 밑에 sum_PNL = sum_PNL + BV_daily_month_profit["daily"] 이거 구할 때, 이미 daily 값에 반영이 되어 있으니까 빼줌
                        # sum_PNL = sum_PNL-PNL

                        #해당 코인을 구매 리스트에서 빼주기 but cnt는 0이 쓰여서, 하루동안 동일 코인을 또 사진 않음
                        BV_coinlist.remove(ticker)
                        # 파일에 리스트를 저장합니다
                        with open(BV_file_path, 'w') as outfile:
                            json.dump(BV_coinlist, outfile)

                        if now_price - BV_pole_point_dict[ticker] > BV_range:
                            BV_range_index = 1
                        if PNL<-loss_cut_ratio*GetInMoney*set_leverage:
                            loss_cut_index = 1
                        if rsi_hour_BTC <= rsi_crit_bottom_BTC:
                            BTC_rsi_index = 1
                        # if rsi_hour_ticker <= rsi_crit_bottom_ticker:
                        #     ticker_rsi_index = 1
                        # if len(BV_coinlist) <= MA_cut_num and  now_price>MA_1m_ticker and revenue_rate > revenue_rate_cut:
                        #     MA_profit_index = 1
                        close_situation = [BV_range_index,loss_cut_index,BTC_rsi_index,ticker_rsi_index,MA_profit_index]
                        Situation_index = close_situation.index(1)
                        line_alert.SendMessage_SP("★트레일링 스탑 : " + ticker +" 진입 cnt : " +str(BV_cnt[ticker]) + "\n 수익률 : " + str(round(revenue_rate*100, 4))+
                                                  " 수익$ : " + str(round(PNL, 4))+ "$" + " 현재가 : " + str(round(now_price, 4))+ "$\n청산 타입 : " +str(Situation_index))

                        # cnt 0의 의미는 진입했다가 -> 청산된 코인을 의미
                        BV_cnt[ticker] = 0
                        with open(BV_cnt_file_path, 'w') as outfile:
                            json.dump(BV_cnt, outfile)

                        # 코인별 승,패,승 누적 달러, 패 누적 달러, 손익비 저장
                        if PNL > 0:
                            BV_daily_month_profit[ticker][0] = BV_daily_month_profit[ticker][0] + 1
                            BV_daily_month_profit[ticker][2] = BV_daily_month_profit[ticker][2] + PNL
                            BV_daily_month_profit[ticker][4] = -BV_daily_month_profit[ticker][2]/BV_daily_month_profit[ticker][3]
                        elif PNL < 0:
                            BV_daily_month_profit[ticker][1] = BV_daily_month_profit[ticker][1] + 1
                            BV_daily_month_profit[ticker][3] = BV_daily_month_profit[ticker][3] + PNL
                            BV_daily_month_profit[ticker][4] = -BV_daily_month_profit[ticker][2] / BV_daily_month_profit[ticker][3]

                        # 파일에 딕셔너리를 저장합니다
                        BV_daily_month_profit["daily"] = BV_daily_month_profit["daily"] + PNL
                        BV_daily_month_profit["month"] = BV_daily_month_profit["month"] + PNL
                        with open(BV_daily_month_profit_type_file_path, 'w') as outfile:
                            json.dump(BV_daily_month_profit, outfile)

            elif amt > 0:
                if now_price >= BV_pole_point_dict[ticker] and status != 'Done':
                # if now_price >= BV_pole_point_dict[ticker] and status != 'Done' and rsi_hour_BTC < rsi_crit_top_BTC and rsi_hour_ticker < rsi_crit_top_ticker:

                    # 이렇게 딕셔너리에 값을 넣어주면 된다.
                    BV_pole_point_dict[ticker] = now_price

                    # 파일에 딕셔너리를 저장합니다
                    with open(BV_pole_point_file_path, 'w') as outfile:
                        json.dump(BV_pole_point_dict, outfile)

                elif status == 'Done':
                    pass

                # 손절 로직 : 자산*(받아들일수있는 손실/투자 코인수)*(코인당 투자 액/자산)*코인수 // 반대로 변동성 만큼 떨어지거나, 투자 금액의 2% 손해 이상 보거나, BTC RSI로 청산하거나, 개별코인 RSI로 청산하거나, 1%이상 이익 봤는데, 진입 코인이 7개 이하고, MA 꺾였을 때
                else:
                    df = myBinance_USDT.GetOhlcv(binanceX, ticker, '1h')  # 시간봉 데이타를 가져온다.
                    BV_range = (float(max(df['high'][-(hour + 25):-(hour + 1)])) - float(min(df['low'][-(hour + 25):-(hour + 1)]))) * k_parameter
                    #손절 로직 : 자산*(받아들일수있는 손실/투자 코인수)*(코인당 투자 액/자산)*코인수
                    # if BV_pole_point_dict[ticker] - now_price > BV_range*loss_cut_range_ratio or PNL<-loss_cut_ratio*GetInMoney*set_leverage or rsi_hour_ticker >= rsi_crit_top_ticker:
                    if PNL < -loss_cut_ratio * GetInMoney * set_leverage or rsi_hour_ticker >= rsi_crit_top_ticker:
                    # if BV_pole_point_dict[ticker] - now_price > BV_range or PNL < -loss_cut_ratio * GetInMoney * set_leverage or rsi_hour_BTC >= rsi_crit_top_BTC or \
                    #         rsi_hour_ticker >= rsi_crit_top_ticker or (len(BV_coinlist) <= MA_cut_num and now_price < MA_1m_ticker and revenue_rate > revenue_rate_cut):
                        # 시장가로 모두 매도!
                        if float(posi['positionAmt']) < 0:
                            params = {'positionSide': 'SHORT'}
                            print(binanceX.create_order(ticker, 'market', 'buy', abs(amt), None, params))
                        elif float(posi['positionAmt']) > 0:
                            params = {'positionSide': 'LONG'}
                            print(binanceX.create_order(ticker, 'market', 'sell', abs(amt), None, params))

                        # 빼주는 이유는 밑에 sum_PNL = sum_PNL + BV_daily_month_profit["daily"] 이거 구할 때, 이미 daily 값에 반영이 되어 있으니까 빼줌
                        sum_PNL = sum_PNL - PNL

                        # 해당 코인을 구매 리스트에서 빼주기 but cnt는 0이 쓰여서, 하루동안 동일 코인을 또 사진 않음
                        BV_coinlist.remove(ticker)
                        # 파일에 리스트를 저장합니다
                        with open(BV_file_path, 'w') as outfile:
                            json.dump(BV_coinlist, outfile)

                        if BV_pole_point_dict[ticker] - now_price > BV_range:
                            BV_range_index = 1
                        if PNL<-loss_cut_ratio*GetInMoney*set_leverage:
                            loss_cut_index = 1
                        # if rsi_hour_BTC >= rsi_crit_top_BTC:
                        #     BTC_rsi_index = 1
                        if rsi_hour_ticker >= rsi_crit_top_ticker :
                            ticker_rsi_index = 1
                        # if len(BV_coinlist) <= MA_cut_num and  now_price<MA_1m_ticker and revenue_rate > revenue_rate_cut:
                        #     MA_profit_index = 1
                        close_situation = [BV_range_index,loss_cut_index,BTC_rsi_index,ticker_rsi_index,MA_profit_index]
                        Situation_index = close_situation.index(1)

                        # 이렇게 손절했다고 메세지를 보낼수도 있다
                        line_alert.SendMessage_SP("\U0001F628트레일링 스탑 : " + ticker + " 진입 cnt : " + str(BV_cnt[ticker]) + "\n 수익률 : " + str(round(revenue_rate * 100, 4)) +
                                                  " 수익$ : " + str(round(PNL, 4)) + "$" + " 현재가 : " + str(round(now_price, 4)) + "$\n청산 타입 : " + str(Situation_index))

                        # cnt 0의 의미는 진입했다가 -> 청산된 코인을 의미
                        BV_cnt[ticker] = 0
                        with open(BV_cnt_file_path, 'w') as outfile:
                            json.dump(BV_cnt, outfile)

                        # 코인별 승,패,승 누적 달러, 패 누적 달러, 손익비 저장
                        if PNL > 0:
                            BV_daily_month_profit[ticker][0] = BV_daily_month_profit[ticker][0] + 1
                            BV_daily_month_profit[ticker][2] = BV_daily_month_profit[ticker][2] + PNL
                            BV_daily_month_profit[ticker][4] = -BV_daily_month_profit[ticker][2] / BV_daily_month_profit[ticker][3]
                        elif PNL < 0:
                            BV_daily_month_profit[ticker][1] = BV_daily_month_profit[ticker][1] + 1
                            BV_daily_month_profit[ticker][3] = BV_daily_month_profit[ticker][3] + PNL
                            BV_daily_month_profit[ticker][4] = -BV_daily_month_profit[ticker][2] / BV_daily_month_profit[ticker][3]


                        # 파일에 딕셔너리를 저장합니다
                        # 일 확정 수익에 넣어 주는 거임
                        BV_daily_month_profit["daily"] = BV_daily_month_profit["daily"] + PNL
                        BV_daily_month_profit["month"] = BV_daily_month_profit["month"] + PNL
                        with open(BV_daily_month_profit_type_file_path, 'w') as outfile:
                            json.dump(BV_daily_month_profit, outfile)

            # if revenue_rate > BV_revenue_dict[ticker] and status != 'Done':
            #
            #     #이렇게 딕셔너리에 값을 넣어주면 된다.
            #     BV_revenue_dict[ticker] = revenue_rate
            #
            #     #파일에 딕셔너리를 저장합니다
            #     with open(revenue_type_file_path, 'w') as outfile:
            #         json.dump(BV_revenue_dict, outfile)
            #
            # elif status == 'Done':
            #     pass
            #
            # #그게 아닌데
            # else:
            #     #고점 수익율 - 스탑 수익율 >= 현재 수익율... 즉 고점 대비 x% 떨어진 상황이라면 트레일링 스탑!!! 모두 매도한다!
            #     if (BV_revenue_dict[ticker] - stop_revenue) >= revenue_rate:
            #         #시장가로 모두 매도!
            #         if float(posi['positionAmt']) < 0:
            #             params = {'positionSide': 'SHORT'}
            #             print(binanceX.create_order(ticker, 'market', 'buy', abs(amt), None, params))
            #         elif float(posi['positionAmt']) > 0:
            #             params = {'positionSide': 'LONG'}
            #             print(binanceX.create_order(ticker, 'market', 'sell', abs(amt), None, params))
            #
            #         BV_daily_month_profit["daily"] = BV_daily_month_profit["daily"] + PNL
            #         BV_daily_month_profit["month"] = BV_daily_month_profit["month"] + PNL
            #
            #         #빼주는 이유는 밑에 sum_PNL = sum_PNL + BV_daily_month_profit["daily"] 이거 구할 때, 이미 daily 값에 반영이 되어 있으니까 빼줌
            #         sum_PNL = sum_PNL-PNL
            #
            #         # 파일에 딕셔너리를 저장합니다
            #         with open(BV_daily_month_profit_type_file_path, 'w') as outfile:
            #             json.dump(BV_daily_month_profit, outfile)
            #
            #         #이렇게 손절했다고 메세지를 보낼수도 있다
            #         line_alert.SendMessage_SP("★트레일링 스탑 : " + ticker + "\n 수익률 : " + str(round(revenue_rate*100,3))+ " 수익$ : " + str(round(PNL, 4))+ "$")

    except Exception as e:
        print("---:", e)
current_time = datetime.now(timezone('Asia/Seoul'))
KR_time=str(current_time)
KR_time_sliced =KR_time[:23]
# 오늘 수익 = 현재 position 수익 + 일 확정 수익
day_PNL = sum_PNL + BV_daily_month_profit["daily"]
# 월 수익 = 현재 position 수익 + 월 확정 수익
month_PNL = sum_PNL + BV_daily_month_profit["month"]

if len(Telegram_Log) !=0 and sum_isolated_cost !=0:
    Telegram_Log_str = str()
    num_type=0
    for key, value in Telegram_Log.items():
        num_type=num_type+1
        key_ticker = key.replace('/USDT', '')
        Telegram_Log_str += str(num_type) + "." + key_ticker + " Status : " + str(value[0])+"\n" \
                            + " 수익률 : "+ str(100*value[1]) + "%" + "\n 수익$ : "+ str(value[2])+ "$" + " 투입액 : "+ str(value[3])+"\n"
    line_alert.SendMessage_BV("  \U0001F4C8\U0001F4C9" +KR_time_sliced+"\U0001F4C8\U0001F4C9  \n\n" +"[요약] \n현 포지션 수익$ : "+ str(round(sum_PNL, 4)) + " \n일 수익$ : "
                              + str(round(day_PNL, 4))+ "\n일 수익률 : " + str(round(day_PNL/(GetInMoney*MaxCoinCnt*set_leverage)*100, 4)) + "% 월 수익$ : "+ str(round(month_PNL, 4))+ "$\n\n"+Telegram_Log_str)
else:
    # 55분
    if hour == hour_crit and minute==min_crit+1:
        line_alert.SendMessage_SP("  \U0001F4C8\U0001F4C9" + KR_time_sliced + "\U0001F4C8\U0001F4C9\n\n" + "[요약] \n일 수익$ : "+ str(round(day_PNL, 4)) + " 월 수익$ : "+ str(round(month_PNL, 4))+
                                  "\n승리 : " + str(BV_daily_month_profit["day_based_win"]) +"  패배 :" + str(BV_daily_month_profit["day_based_lose"]) +
                                  "  승률 : " + str(round(100*BV_daily_month_profit["day_based_win"]/(BV_daily_month_profit["day_based_lose"]+BV_daily_month_profit["day_based_win"]), 4))+
                                  "\n누적 승리액 $ : " + str(round(BV_daily_month_profit["cumulative_win_dollor"], 4)) + "  누적 패배액 $ : " + str(round(BV_daily_month_profit["cumulative_lose_dollor"], 4)) +
                                  "\n누적 손익비 : " + str(round(-BV_daily_month_profit["cumulative_win_dollor"]/BV_daily_month_profit["cumulative_lose_dollor"], 4)))
    # 56,57,58,59분
    else:
        line_alert.SendMessage_BV("  \U0001F4C8\U0001F4C9" + KR_time_sliced + "\U0001F4C8\U0001F4C9\n\n" + "[요약] \n일 수익$ : " + str(round(day_PNL, 4)) + " 월 수익$ : " + str(round(month_PNL, 4)) +
                                  "\n승리 : " + str(BV_daily_month_profit["day_based_win"]) + "  패배 :" + str(BV_daily_month_profit["day_based_lose"]) +
                                  "  승률 : " + str(round(100 * BV_daily_month_profit["day_based_win"] / (BV_daily_month_profit["day_based_lose"] + BV_daily_month_profit["day_based_win"]), 4)) +
                                  "\n누적 승리액 $ : " + str(round(BV_daily_month_profit["cumulative_win_dollor"], 4))+ "  누적 패배액 $ : " + str(round(BV_daily_month_profit["cumulative_lose_dollor"], 4)) +
                                  "\n누적 손익비 : " + str(round(-BV_daily_month_profit["cumulative_win_dollor"] / BV_daily_month_profit["cumulative_lose_dollor"], 4)))


if hour == hour_crit and minute == min_crit:
    if day_PNL > 0:
        BV_daily_month_profit["day_based_win"] = BV_daily_month_profit["day_based_win"] + 1
        BV_daily_month_profit["cumulative_win_dollor"] = BV_daily_month_profit["cumulative_win_dollor"] + day_PNL
        BV_daily_month_profit["totol_profit_ratio"]= -BV_daily_month_profit["cumulative_win_dollor"]/BV_daily_month_profit["cumulative_lose_dollor"]
    elif day_PNL < 0:
        BV_daily_month_profit["day_based_lose"] = BV_daily_month_profit["day_based_lose"] + 1
        BV_daily_month_profit["cumulative_lose_dollor"] = BV_daily_month_profit["cumulative_lose_dollor"] + day_PNL
        BV_daily_month_profit["totol_profit_ratio"] = -BV_daily_month_profit["cumulative_win_dollor"] / BV_daily_month_profit["cumulative_lose_dollor"]
    else:
        pass

    BV_daily_month_profit["month"] = month_PNL
    day_PNL = 0
    with open(BV_daily_month_profit_type_file_path, 'w') as outfile:
        json.dump(BV_daily_month_profit, outfile)