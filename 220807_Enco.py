#-*-coding:utf-8 -*-
import myUpbit   #내가 만든 함수들이 들어있는 모듈
import time
import pyupbit
import sys, os
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키
import dollar_future_fuction as dff

import line_alert #라인,텔레그램 메세지를 보내기 위함!
import traceback
import ccxt
import requests
import myBinance
import json
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup as bs
import platform

if platform.system() == 'Windows':
    Month_profit_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Month_profit.json"
    Kimplist_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Kimplist.json"
    Situation_flag_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Situation_flag.json"
    Krate_ExClose_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Krate_ExClose.json"
    Krate_total_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Krate_total.json"
    top_file_path = "C:\\Users\world\PycharmProjects\Crypto\TopCoinList.json"
    Trade_infor_path = "C:\\Users\world\PycharmProjects\Crypto\Trade_infor.json"
    BUSD_MA_path = "C:\\Users\world\PycharmProjects\Crypto\BUSD_MA.json"
    Before_amt_path = "C:\\Users\world\PycharmProjects\Crypto\Before_amt.json"
    Before_amt_upbit_path = "C:\\Users\world\PycharmProjects\Crypto\Before_amt_upbit.json"
    Before_price_path = "C:\\Users\world\PycharmProjects\Crypto\Before_price.json"
    Before_price_upbit_path = "C:\\Users\world\PycharmProjects\Crypto\Before_price_upbit.json"
    dollar_rate_path = "C:\\Users\world\PycharmProjects\Crypto\dollar_rate.json"
else:
    Month_profit_type_file_path = "/var/autobot/Month_profit.json"
    Kimplist_type_file_path = "/var/autobot/Kimplist.json"
    Situation_flag_type_file_path = "/var/autobot/Situation_flag.json"
    Krate_ExClose_type_file_path = "/var/autobot/Krate_ExClose.json"
    Krate_total_type_file_path = "/var/autobot/Krate_total.json"
    top_file_path = "/var/autobot/TopCoinList.json"
    Trade_infor_path = "/var/autobot/Trade_infor.json"
    BUSD_MA_path = "/var/autobot/BUSD_MA.json"
    Before_amt_path = "/var/autobot/Before_amt.json"
    Before_amt_upbit_path = "/var/autobot/Before_amt_upbit.json"
    Before_price_path = "/var/autobot/Before_price.json"
    Before_price_upbit_path = "/var/autobot/Before_price_upbit.json"
    dollar_rate_path = "/var/autobot/dollar_rate.json"

""" Tether 가격은 더이상 쓸 필요가 없음
page_USDT = requests.get("https://coinmarketcap.com/ko/currencies/tether/")
soup_USDT = bs(page_USDT.text, "html.parser")
str_TetherKRW = soup_USDT.select_one('div.priceValue span').get_text()
TetherKRW=float(str_TetherKRW[1]+str_TetherKRW[3:9])
"""

# # BUSD 가격 크롤링 해서 가지고 옴
# page_BUSD = requests.get("https://coinmarketcap.com/ko/currencies/binance-usd/")
# soup_BUSD = bs(page_BUSD.text, "html.parser")
# str_BUSDKRW = soup_BUSD.select_one('div.priceValue span').get_text()
# BUSDKRW=float(str_BUSDKRW[1]+str_BUSDKRW[3:9])

# # BUSD 24시간 Range로 평균 가격 가지고 오기
# str_BUSDKRW_range=soup_BUSD.select('span.sc-d5c68954-5')
#
# str_BUSDKRW_lower = str_BUSDKRW_range[0].get_text()
# BUSDKRW_lower = float(str_BUSDKRW_lower[1]+str_BUSDKRW_lower[3:9])
#
# str_BUSDKRW_upper = str_BUSDKRW_range[1].get_text()
# BUSDKRW_upper = float(str_BUSDKRW_upper[1]+str_BUSDKRW_upper[3:9])
#
# BUSDKRW_Day_average = (BUSDKRW_lower+BUSDKRW_upper)*0.5

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = "aHztphf3UiWBHLhte78Rjk1kNBM8iGPRJNtVyxje"
Upbit_ScretKey = "BMzxKxOBJAbz1pB3O26AxjxLZbE9n4EygQ04Zb8d"

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)

time.sleep(0.05)

# Invest_Rate = 0.21
minimum_profit_rate = -0.002
set_leverage = 3
# profit_rate_criteria 기본 값 -> 아래에 함수에 의해서 바뀜
profit_rate_criteria = 1.5
# 환율이 너무 올라서 물타는 경우는 막기 위한 margin값
won_rate_margin = 5
# Krate_interval 물타기 범위 값
Krate_interval = 0.35
Krate_interval_2 = Krate_interval+0.09
Krate_interval_getin = 0.25
AD_criteria = 95
Kimp_crit = 1.2
Stop_price_percent = 0.97
# close_criteria 적어도 이 수치보단 클 때 팔기
close_criteria = 1.2
# 1회 진입 달러 수, ex. GetInMoney 400 달러면 레버리지 고려시, 1200달러 한번에 넣는 거임 // 아래의 값은 그냥 기본 값 넣어준거지 이와 같이 사지는 건 아님
GetInMoney = 333
avoid_liquid_ratio = 1.05
# AD_weight_list = [1, 1.2, 1.3, 1.2, 0.9, 0.8, 0.6, 0.6]
AD_weight_list = [1, 1, 1, 1, 1, 1, 1, 1]

# 바이낸스 업비트 평균 커미션 (0.0003+0.0005)/2
binance_commission = 0.0003
upbit_commission = 0.0005
commission = (upbit_commission + binance_commission) / 2
# profit_range= [3, 1]
# average_range = [-2,2]

profit_range = [1.4, 1.1]
average_range = [-2, Kimp_crit]

# BUSDKRW_MA_value = sum(BUSDKRW_MA_List) / len(BUSDKRW_MA_List)
# binance 객체 생성

# 잔고 데이타 가져오기
# balance_binanace = binanceX.fetch_balance(params={"type": "future"})

upbit_diff_BTC = 0
upbit_remain_money = 0

min_temp = 0
hour_temp = 0
big_kimp_flag = 0
small_kimp_flag = 0

while True:
    try:
        # 시간 정보를 가져옵니다. 아침 9시의 경우 서버에서는 hour변수가 0이 됩니다.
        time_info = time.gmtime()
        hour = time_info.tm_hour
        min = time_info.tm_min

        # won_rate = myUpbit.upbit_get_usd_krw()
        won_rate=dff.get_exchange_rate()

        if min_temp ==min:
            min_flag = 0
        else:
            min_flag = 1
        min_temp = min

        if hour_temp != hour:
            big_kimp_flag = 0
            small_kimp_flag = 0

        hour_temp = hour
        # 한국시간 9시 -> 0
        hour_crit = 20
        min_crit = 25

        Month_profit = list()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Month_profit_type_file_path, 'r', encoding="utf-8") as json_file:
                Month_profit = json.load(json_file)

        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 0")

        # 김프 리스트를 저장하기 위한 부분, 만약 처음 돌려서 파일이 존재하지 않으면, exception 처리하고 밑에서 따로 저장함
        Kimplist = list()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Kimplist_type_file_path, 'r', encoding="utf-8") as json_file:
                Kimplist = json.load(json_file)

        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 1")

        # 김프 리스트를 저장하기 위한 부분, 만약 처음 돌려서 파일이 존재하지 않으면, exception 처리하고 밑에서 따로 저장함
        Situation_flag = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Situation_flag_type_file_path, 'r', encoding="utf-8") as json_file:
                Situation_flag = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 2")

        # 전날 close 값 불러오기 위함. 만약 처음 돌려서 파일이 존재하지 않으면, exception 처리하고 밑에서 따로 저장함
        Krate_ExClose = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Krate_ExClose_type_file_path, 'r', encoding="utf-8") as json_file:
                Krate_ExClose = json.load(json_file)

        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 3")

        # 거래 김프 total 정보. 만약 처음 돌려서 파일이 존재하지 않으면, exception 처리하고 밑에서 따로 저장함
        Krate_total = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Krate_total_type_file_path, 'r', encoding="utf-8") as json_file:
                Krate_total = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 4")

        Trade_infor = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Trade_infor_path, 'r', encoding="utf-8") as json_file:
                Trade_infor = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 5")

        Before_amt = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Before_amt_path, 'r', encoding="utf-8") as json_file:
                Before_amt = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 6")

        Before_amt_upbit = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Before_amt_upbit_path, 'r', encoding="utf-8") as json_file:
                Before_amt_upbit = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 7")

        dollar_rate = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(dollar_rate_path, 'r', encoding="utf-8") as json_file:
                dollar_rate = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 8")

        Before_price = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Before_price_path, 'r', encoding="utf-8") as json_file:
                Before_price = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 9")

        Before_price_upbit = dict()
        try:
            # 이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
            with open(Before_price_upbit_path, 'r', encoding="utf-8") as json_file:
                Before_price_upbit = json.load(json_file)
        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            print("Exception by First 10")

        Telegram_Log = dict()

        # TopCoinList N 개를 저장시키기 위한 Code
        TopCoinList = list()
        try:
            with open(top_file_path, "r", encoding="utf-8") as json_file:
                TopCoinList = json.load(json_file)
                if hour == hour_crit and min % 60 == min_crit and len(Kimplist) == 0:
                    TopCoinList = myUpbit.GetTopCoinList("day", 30)

                    setForExclose = set(Krate_ExClose.keys())
                    setForTotal = set(Krate_total.keys())
                    setForFlag = set(Situation_flag.keys())
                    setForBefore = set(Before_amt.keys())
                    setForBefore_upbit = set(Before_amt_upbit.keys())
                    setForBefore_price = set(Before_price.keys())
                    setForBefore_price_upbit = set(Before_price_upbit.keys())

                    setdollar_rate = set(dollar_rate.keys())
                    setForTopcoin = set(TopCoinList)

                    # 기존 list에 있는 값이랑 차이 있는 값에 대한 list를 만듦
                    setDifference_Exclose = list(setForExclose.difference(setForExclose))
                    setDifference_Total = list(setForTotal.difference(setForTotal))
                    setDifference_Flag = list(setForFlag.difference(setForFlag))
                    setDifference_Before = list(setForBefore.difference(setForBefore))
                    setDifference_Before_upbit = list(setForBefore_upbit.difference(setForBefore_upbit))
                    setDifference_Before_price = list(setForBefore_price.difference(setForBefore_price))
                    setDifference_Before_price_upbit = list(setForBefore_price_upbit.difference(setForBefore_price_upbit))
                    setDifference_dollar_rate = list(setdollar_rate.difference(setdollar_rate))

                    for remove_element_Exclose in setDifference_Exclose:
                        if remove_element_Exclose in Krate_ExClose:
                            del Krate_ExClose[remove_element_Exclose]

                    for remove_element_Total in setDifference_Total:
                        if remove_element_Total in Krate_total:
                            del Krate_total[remove_element_Total]

                    for remove_element_Flag in setDifference_Flag:
                        if remove_element_Flag in Situation_flag:
                            del Situation_flag[remove_element_Flag]

                    for remove_element_Before in setDifference_Before:
                        if remove_element_Before in Before_amt:
                            del Before_amt[remove_element_Before]

                    for remove_element_Before_upbit in setDifference_Before_upbit:
                        if remove_element_Before_upbit in Before_amt_upbit:
                            del Before_amt_upbit[remove_element_Before_upbit]

                    for remove_element_Before_price in setDifference_Before_price:
                        if remove_element_Before_price in Before_price:
                            del Before_price[remove_element_Before_price]

                    for remove_element_Before_price_upbit in setDifference_Before_price_upbit:
                        if remove_element_Before_price_upbit in Before_price_upbit:
                            del Before_price_upbit[remove_element_Before_price_upbit]

                    for remove_element_dollar_rate in setDifference_dollar_rate:
                        if remove_element_dollar_rate in dollar_rate:
                            del dollar_rate[remove_element_dollar_rate]

                    with open(top_file_path, 'w', encoding="utf-8") as outfile:
                        json.dump(TopCoinList, outfile)
                    with open(Krate_ExClose_type_file_path, 'w') as outfile:
                        json.dump(Krate_ExClose, outfile)
                    with open(Krate_total_type_file_path, 'w') as outfile:
                        json.dump(Krate_total, outfile)
                    with open(Situation_flag_type_file_path, 'w') as outfile:
                        json.dump(Situation_flag, outfile)
                    with open(Before_amt_path, 'w') as outfile:
                        json.dump(Before_amt, outfile)
                    with open(Before_amt_upbit_path, 'w') as outfile:
                        json.dump(Before_amt_upbit, outfile)

                    with open(Before_price_path, 'w') as outfile:
                        json.dump(Before_price, outfile)
                    with open(Before_price_upbit_path, 'w') as outfile:
                        json.dump(Before_price_upbit, outfile)

                    with open(dollar_rate_path, 'w') as outfile:
                        json.dump(dollar_rate, outfile)

        except Exception as e:
            TopCoinList = myUpbit.GetTopCoinList("day", 40)
            print("Exception by First")

        # BUSDKRW_MA_List = list()
        # try:
        #     #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
        #     with open(BUSD_MA_path, 'r', encoding="utf-8") as json_file:
        #         BUSDKRW_MA_List = json.load(json_file)
        #         if hour == hour_crit and min % 60 == min_crit:
        #             del BUSDKRW_MA_List[0]
        #             BUSDKRW_MA_List.append(BUSDKRW_Day_average)
        #             with open(BUSD_MA_path, 'w', encoding="utf-8") as outfile:
        #                 json.dump(BUSDKRW_MA_List, outfile)
        #
        #
        # except Exception as e:
        #     #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        #     print("Exception by First 6")

        binanceX = ccxt.binance(config={'apiKey': Binance_AccessKey, 'secret': Binance_ScretKey, 'enableRateLimit': True, 'options': {'defaultType': 'future','recvWindow': 15000}})
        # 업비트에서 비트코인 사기 전까지 아래 값은 0이지
        # upbit_diff_BTC = float(myUpbit.NumOfTickerCoin(balance_upbit, "KRW-BTC")) * (pyupbit.get_current_price("KRW-BTC") - float(myUpbit.GetAvgBuyPrice(balance_upbit, "KRW-BTC")))

        # binance API의 서버 시간을 가져옴
        server_time = binanceX.fetch_time()
        # 로컬 컴퓨터의 시간을 가져옴
        local_time = int(time.time() * 1000)
        # 서버 시간과 로컬 시간의 차이를 계산하여 nonce 값을 설정
        nonce = max(server_time, local_time)

        # 내가 가진 잔고 데이터를 다 가져온다.
        balance_upbit = upbit.get_balances()

        # won_rate = myUpbit.upbit_get_usd()
        # 김프 리스트에 있는 애들 중 포지션 없는 애들은 다 지움
        for jj in Kimplist:
            if not myUpbit.IsHasCoin(balance_upbit, jj):
                del Krate_ExClose[jj]
                del Krate_total[jj]
                del Situation_flag[jj]
                del Before_amt[jj]
                del Before_amt_upbit[jj]
                del Before_price[jj]
                del Before_price_upbit[jj]
                del dollar_rate[jj]
                del Trade_infor[jj]
                Kimplist.remove(jj)

                with open(Krate_ExClose_type_file_path, 'w') as outfile:
                    json.dump(Krate_ExClose, outfile)
                with open(Krate_total_type_file_path, 'w') as outfile:
                    json.dump(Krate_total, outfile)
                with open(Situation_flag_type_file_path, 'w') as outfile:
                    json.dump(Situation_flag, outfile)
                with open(Trade_infor_path, 'w') as outfile:
                    json.dump(Trade_infor, outfile)
                with open(Kimplist_type_file_path, 'w') as outfile:
                    json.dump(Kimplist, outfile)
                with open(Before_amt_path, 'w') as outfile:
                    json.dump(Before_amt, outfile)
                with open(Before_amt_upbit_path, 'w') as outfile:
                    json.dump(Before_amt_upbit, outfile)
                with open(Before_price_path, 'w') as outfile:
                    json.dump(Before_price, outfile)
                with open(Before_price_upbit_path, 'w') as outfile:
                    json.dump(Before_price_upbit, outfile)
                with open(dollar_rate_path, 'w') as outfile:
                    json.dump(dollar_rate, outfile)

        for upbit_asset in balance_upbit:
            if upbit_asset['currency'] == 'KRW':
                upbit_remain_money = float(upbit_asset['balance'])
            else:
                continue

        characters = "KRW-"

        # 거래에서 제외할 코인
        # try:
        #     TopCoinList.remove("KRW-TRX")
        #     TopCoinList.remove("KRW-WEMIX")
        #     TopCoinList.remove("KRW-WAVES")
        # except Exception as e:
        #     print("BTC remove error", e)

        # 거래 순서를 김프 평단이 낮은 애부터 거래 되도록 하기 위함...
        if len(Krate_total) != 0:

            Krate_aver_total = dict()
            Traded_sorted_list = list()

            for temp_ticker in Krate_total:
                temp_Krate_dummy = Krate_total[temp_ticker]
                while False in temp_Krate_dummy:
                    temp_Krate_dummy.remove(False)
                Krate_average = sum(temp_Krate_dummy) / len(temp_Krate_dummy)
                Krate_aver_total[temp_ticker] = Krate_average

            Traded_list = sorted(Krate_aver_total.items(), key=lambda item: item[1])
            # 평단 높은 애 먼저 물타고 싶으면 아래 주석을 푼다.
            # Traded_list = sorted(Krate_aver_total.items(), key=lambda item: item[1], reverse = True)
            for ii in Traded_list:
                Traded_sorted_list.append(ii[0])

            s = set(Traded_sorted_list)
            Rest_topcoin = [x for x in TopCoinList if x not in s]

            Sorted_topcoinlist = Traded_sorted_list + Rest_topcoin

        else:
            Sorted_topcoinlist = TopCoinList
        # 진입 티커 갯수 늘릴 거면, CNT

        Kimp_target_coin = ['KRW-BTC', 'KRW-XRP', 'KRW-ETH', 'KRW-SOL', 'KRW-DOGE']
        CoinCnt = len(Kimp_target_coin)
        # Kimp_target_coin = ['KRW-XRP','KRW-ETH','KRW-DOGE']
        remove_coin = list(set(Sorted_topcoinlist) - set(Kimp_target_coin))
        Sorted_topcoinlist = list(set(Sorted_topcoinlist) - set(remove_coin))

        # 티커별 for문 루프
        for ticker_upbit in Sorted_topcoinlist:

            # if Trade_infor['general'][0] == 0:
            #     continue
            time.sleep(0.1)
            now_price_upbit = pyupbit.get_current_price(ticker_upbit)

            if now_price_upbit < 10 and myUpbit.CheckCoinInList(Kimplist, ticker_upbit) == False:
                continue
            ticker_temp = ticker_upbit.replace('KRW-', '')
            ticker_binance = ticker_temp + '/BUSD'
            ticker_binance_orderbook = ticker_temp + 'BUSD'


            time.sleep(0.05)
            now_price_binance = myBinance.GetCoinNowPrice(binanceX, ticker_binance)
            # Krate = ((now_price_upbit / (now_price_binance * won_rate)) - 1) * 100

            Target_Coin_Symbol = ticker_binance.replace("/", "")

            balance_binanace = binanceX.fetch_balance(params={"type": "future",'adjustForTimeDifference': True})
            for posi in balance_binanace['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                    print(posi)
                    amt_s = float(posi['positionAmt'])
                    entryPrice_s = float(posi['entryPrice'])
                    leverage = float(posi['leverage'])
                    isolated = posi['isolated']
                    unrealizedProfit = float(posi['unrealizedProfit'])
                    break

            url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'
            time.sleep(0.05)
            binance_orderbook_data = requests.get(url).json()
            time.sleep(0.05)
            Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney / now_price_binance * set_leverage))

            # 바이낸스 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
            binance_order_index = 0
            binance_order_Nsum = 0
            for price_i, num_i in binance_orderbook_data['bids']:
                binance_order_Nsum += float(num_i)
                if binance_order_Nsum > abs(Buy_Amt):
                    break
                binance_order_index += 1
            binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

            # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
            time.sleep(0.05)
            orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
            time.sleep(0.05)
            upbit_order_index = 0
            upbit_order_Nsum = 0

            for upbit_order_data in orderbook_upbit['orderbook_units']:
                upbit_order_Nsum += upbit_order_data['ask_size']
                if upbit_order_Nsum > abs(Buy_Amt):
                    break
                upbit_order_index += 1
            upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

            # 바이낸스에서 팔 때 슬리피지는 다르게 해줘야지
            binance_order_index_close = 0
            binance_order_Nsum_close = 0
            for price_i, num_i in binance_orderbook_data['asks']:
                binance_order_Nsum_close += float(num_i)

                if binance_order_Nsum_close > abs(amt_s):
                    break
                binance_order_index_close += 1  # 버퍼로 하나 더해줌
            binance_order_standard_close = float(binance_orderbook_data['asks'][binance_order_index_close][0])

            # 업비트에서 팔 때 슬리피지는 다르게 해줘야지
            upbit_order_index_close = 0
            upbit_order_Nsum_close = 0

            for upbit_order_data in orderbook_upbit['orderbook_units']:
                upbit_order_Nsum_close += upbit_order_data['bid_size']

                if upbit_order_Nsum_close > abs(amt_s):
                    break
                upbit_order_index_close += 1
            upbit_order_standard_close = orderbook_upbit['orderbook_units'][upbit_order_index_close]['bid_price']

            ADMoney = Buy_Amt * upbit_order_standard

            # 김프를 절대 환율로 보지 않게 다시 수정
            # if ticker_upbit in Kimplist:
            #     Krate = ((upbit_order_standard / (binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
            #     Krate_close = ((upbit_order_standard_close / (binance_order_standard_close * Trade_infor[ticker_upbit][0])) - 1) * 100
            # else:
            #     Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
            #     Krate_close = ((upbit_order_standard_close / (binance_order_standard_close * won_rate)) - 1) * 100

            Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
            Krate_close = ((upbit_order_standard_close / (binance_order_standard_close * won_rate)) - 1) * 100

            if ticker_upbit == 'KRW-BTC' and Krate < -0.7 and small_kimp_flag==0:
                small_kimp_flag=1
                now_price_upbit_TRX = pyupbit.get_current_price('KRW-TRX')
                now_price_binance_TRX = myBinance.GetCoinNowPrice(binanceX, 'TRX/BUSD')
                Krate_TRX = ((now_price_upbit_TRX / (now_price_binance_TRX * won_rate)) - 1) * 100
                line_alert.SendMessage_SP("[\U0001F4B5大역프 알림] : " + str(round(Krate, 2)) + "\n[트론 역프] : " + str(round(Krate_TRX, 2)) + "\n[환율] : " + str(round(won_rate, 2)))
            elif ticker_upbit == 'KRW-BTC' and Krate > 4 and big_kimp_flag==0:
                big_kimp_flag=1
                now_price_upbit_TRX = pyupbit.get_current_price('KRW-TRX')
                now_price_binance_TRX = myBinance.GetCoinNowPrice(binanceX, 'TRX/BUSD')
                Krate_TRX = ((now_price_upbit_TRX / (now_price_binance_TRX * won_rate)) - 1) * 100
                line_alert.SendMessage_SP("[\U0001F4B5大김프 알림] : " + str(round(Krate, 2)) + "\n[트론 김프] : " + str(round(Krate_TRX, 2)) + "\n[환율] : " + str(round(won_rate, 2)))

            """
            if myUpbit.IsHasCoin(balance_upbit,ticker_upbit):
                profit_rate = 100 * ((upbit_order_standard - myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)) * myUpbit.NumOfTickerCoin(
                    balance_upbit, ticker_upbit) - won_rate * amt_s * (entryPrice_s - binance_order_standard)) / (myUpbit.NumOfTickerCoin(balance_upbit, ticker_upbit) 
                    * myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) - amt_s * entryPrice_s * won_rate)
            """

            # 매수 Krate의 평균을 구하기 위한 code
            if ticker_upbit in Krate_total:
                temp_Krate_dummy2 = Krate_total[ticker_upbit]
                while False in temp_Krate_dummy2:
                    temp_Krate_dummy2.remove(False)
                    Krate_average = sum(temp_Krate_dummy2) / len(temp_Krate_dummy2)
                TryNumber = len(temp_Krate_dummy2)
            else:
                # Krate_total[ticker_upbit] = [2,2,2,2,2]
                # Krate_list = list(filter(None, Krate_total[ticker_upbit]))
                Krate_average = 20

            # 위에서 Krate_total -100 다 remove시켜서 다시 가지고 옴
            with open(Krate_total_type_file_path, 'r', encoding="utf-8") as json_file:
                Krate_total = json.load(json_file)

            # TopCoinList가 바뀌어서 ExClose에 새로 넣어줘야할 때
            if ticker_upbit in Krate_ExClose:
                pass
            else:
                Krate_ExClose[ticker_upbit] = Krate
                with open(Krate_ExClose_type_file_path, 'w') as outfile:
                    json.dump(Krate_ExClose, outfile)

            # 종가를 저장하는 로직 // 적어도 전날 기준 몇 이하에서 사도록 코딩
            if hour == hour_crit and min % 60 == min_crit:
                Krate_ExClose[ticker_upbit] = Krate
                with open(Krate_ExClose_type_file_path, 'w') as outfile:
                    json.dump(Krate_ExClose, outfile)

                Trade_infor['general'][2] = Trade_infor['general'][3]
                Trade_infor['general'][3] = won_rate
                with open(Trade_infor_path, 'w') as outfile:
                    json.dump(Trade_infor, outfile)

            leverage = 0  # 레버리지
            isolated = False  # 격리모드인지
            cross = False
            Target_Coin_Symbol = ticker_binance.replace("/", "")

            #################################################################################################################
            # 레버리지 셋팅
            if leverage != set_leverage:

                try:
                    print(binanceX.fapiPrivate_post_leverage(
                        {'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                except Exception as e:
                    print("Exception:", e)

            #################################################################################################################
            # 격리 모드로 설정  Exception: binance {"code":-4046,"msg":"No need to change margin type."}
            if cross == False:
                try:
                    print(binanceX.fapiPrivate_post_margintype(
                        {'symbol': Target_Coin_Symbol, 'marginType': 'CROSSED'}))
                except Exception as e:
                    print("Exception:", e)
            #################################################################################################################

            # 전략에 의해 매수 했고

            if myUpbit.CheckCoinInList(Kimplist, ticker_upbit) == True:
                # 따라서 잔고도 있다.
                if myUpbit.IsHasCoin(balance_upbit, ticker_upbit) == True:

                    """
                    if Krate_average<=0:
                        profit_rate_criteria = 1.65
                    elif 0<Krate_average<=1:
                        profit_rate_criteria = 1.4
                    elif 1<Krate_average<=2:
                        profit_rate_criteria = 1.2
                    elif 2 < Krate_average <= 2.5:
                        profit_rate_criteria = 1.1
                    else:
                        profit_rate_criteria = 1.0
                    """
                    Situation_index = Situation_flag[ticker_upbit].index(False)
                    profit_rate_criteria = myUpbit.ProfitReturn(profit_range, average_range, Krate_total[ticker_upbit][Situation_index - 1])

                    upbit_diff = float(myUpbit.NumOfTickerCoin(balance_upbit, ticker_upbit)) * (upbit_order_standard_close - float(myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit)))

                    warning_price_binance = entryPrice_s * (1 + 1 / set_leverage) * 0.95
                    if warning_price_binance - entryPrice_s == 0:
                        warning_percent = 0
                    else:
                        warning_percent = round((now_price_binance - entryPrice_s) / (warning_price_binance - entryPrice_s) * 100, 1)
                    if warning_percent < 0:
                        warning_percent = 0.0

                    if warning_percent > 200:
                        line_alert.SendMessage_SP("[Stoploss 경고] : " + str(ticker_upbit[4:]) + " [Warning %] : " + str(round(warning_percent, 2)) + " %")

                    upbit_invested_money = myUpbit.GetCoinNowMoney(balance_upbit, ticker_upbit)

                    # 수익화  // 아래 주석은 절대 김프로 수익화 할 때임

                    # if (Krate_close > close_criteria and Krate_close > Krate_ExClose[ticker_upbit]+0.1 and Krate_close - Krate_average > profit_rate_criteria) or \
                    #         (unrealizedProfit*won_rate+upbit_diff-upbit_invested_money*2*commission)>-200000:
                    # and Krate - Krate_average <= profit_rate*2.2:
                    # 최종 물탄 틱 기준 profit
                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'
                    binance_orderbook_data = requests.get(url).json()
                    # 바이낸스에서 팔 때 슬리피지는 다르게 해줘야지
                    binance_order_index_close = 0
                    binance_order_Nsum_close = 0
                    for price_i, num_i in binance_orderbook_data['asks']:
                        binance_order_Nsum_close += float(num_i)

                        if binance_order_Nsum_close > abs(amt_s):
                            break
                        binance_order_index_close += 1  # 버퍼로 하나 더해줌
                    binance_order_standard_close = float(binance_orderbook_data['asks'][binance_order_index_close][0])

                    # 업비트에서 팔 때 슬리피지는 다르게 해줘야지
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index_close = 0
                    upbit_order_Nsum_close = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum_close += upbit_order_data['bid_size']

                        if upbit_order_Nsum_close > abs(amt_s):
                            break
                        upbit_order_index_close += 1
                    upbit_order_standard_close = orderbook_upbit['orderbook_units'][upbit_order_index_close]['bid_price']

                    # Before_price_upbit[ticker_upbit][Situation_index - 1] 여기에 저장되는 가격이 실제 마지막 틱 구매 평단을 제대로 반영을 못하고 있음. 230512 Ada, 근데 왜 실제 청산했을 때는 수익이 더 정확하지... ?
                    # now_profit을 이전에 구매한 값 기준 및 호가창 계산 한 걸 기반으로 정확하게 해보려고 했으나, 도지코인 같은 경우 내가 체결되는 가격을 정확하게 계산하기 어려움 -> Before price가 부정확
                    # 그래서 now_profit을 그냥, UnRealizedProfit 값 가져온 거에 수수료를 보수적으로 때려서 계산하는 로직으로 변경 -> 원래 commission * 4 였는데 * 6으로 변경

                    # now_profit = (upbit_order_standard_close - Before_price_upbit[ticker_upbit][Situation_index - 1]) * Before_amt_upbit[ticker_upbit][Situation_index - 1] + \
                    #              (Before_price[ticker_upbit][Situation_index - 1] - binance_order_standard_close) * Before_amt[ticker_upbit][Situation_index - 1] * won_rate \
                    #              - 4 * upbit_order_standard_close * Before_amt_upbit[ticker_upbit][Situation_index - 1] * commission

                    now_profit = unrealizedProfit * won_rate + upbit_diff - upbit_invested_money * 6 * commission

                    #Krate_close 한번 다시 업데이트
                    Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
                    Krate_close = ((upbit_order_standard_close / (binance_order_standard_close * won_rate)) - 1) * 100

                    Telegram_Log[ticker_upbit] = [round(Krate_close, 2), round(Krate_average, 2), round(Krate_total[ticker_upbit][Situation_index - 1] + profit_rate_criteria, 2), TryNumber - 1,
                                                  round((unrealizedProfit * won_rate - 2*upbit_invested_money * binance_commission) / 10000, 2), round((upbit_diff - 2*upbit_invested_money * upbit_commission) / 10000, 2),
                                                  round((unrealizedProfit * won_rate + upbit_diff - upbit_invested_money * 4 * commission) / 10000, 2), warning_percent, round(Krate, 2),
                                                  round(Krate_total[ticker_upbit][Situation_index - 1], 2), round(now_profit / 10000, 2), round((Before_amt_upbit[ticker_upbit][Situation_index - 1] * now_price_upbit * (profit_rate_criteria + 0.15) / 100) / 10000, 2)]

                    # 김프 절대 환율에서 바꿈
                    # if (Krate_close > close_criteria and Krate_close > Krate_ExClose[ticker_upbit]+0.1 and Krate_close - Krate_average > profit_rate_criteria) or \
                    #         (unrealizedProfit*won_rate+upbit_diff-upbit_invested_money*2*commission)>-200000:

                    #수익화
                    # [(수익이 -지만, 김프 기준을 초과 달성) or (수익이 +고, 김프 기준 달성) or (환 상승 포함, 단순히 김프 수익이 초과 달성) ] and [투자 기본 치 넘어야, 단순히 기준치 이상의 투자를 했는지 보는 거임]
                    # 환 선물로 햇지하면서 환 상승에 의한 단순 김프 수익 초과시에는 청산 안하게 바꿈 -> change
                    if ((now_profit < 0 and Krate_close - Krate_total[ticker_upbit][Situation_index - 1] > profit_rate_criteria + 0.2) or (now_profit > 0 and Krate_close - Krate_total[ticker_upbit][Situation_index - 1] > profit_rate_criteria) \
                        or (now_profit > Before_amt_upbit[ticker_upbit][Situation_index - 1] * now_price_upbit * (profit_rate_criteria + 0.15) / 100) )\
                        and now_price_upbit * upbit.get_balance(ticker_upbit) / Situation_index > 5500:

                    # if ((now_profit < 0 and Krate_close - Krate_total[ticker_upbit][Situation_index - 1] > profit_rate_criteria + 0.2) or (now_profit > 0 and Krate_close - Krate_total[ticker_upbit][Situation_index - 1] > profit_rate_criteria)) \
                    #         and now_price_upbit * upbit.get_balance(ticker_upbit) / Situation_index > 5500:

                    # # (김프 기준을 넘고, 최소 수익 기준 넘고) or (단순 수익이 기준치 이상 나면 청산)
                    # if ((Krate_close - Krate_total[ticker_upbit][Situation_index - 1] > profit_rate_criteria
                    #     and now_profit > Before_amt_upbit[ticker_upbit][Situation_index - 1] * now_price_upbit * minimum_profit_rate) \
                    #     or now_profit > Before_amt_upbit[ticker_upbit][Situation_index - 1] * now_price_upbit * (profit_rate_criteria + 0.05) / 100) \
                    #         and now_price_upbit * upbit.get_balance(ticker_upbit) / Situation_index > 5500:

                            # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                            params = {'positionSide': 'SHORT'}
                            # binanceX.cancel_all_orders(ticker_binance)
                            # print(binanceX.create_order(ticker_binance, 'limit', 'buy', abs(amt_s), now_price_binance, params))
                            # sell_Amt = float(binanceX.amount_to_precision(ticker_binance, amt_s / Situation_index))

                            sell_Amt = float(Before_amt[ticker_upbit][Situation_index - 1])
                            print(binanceX.create_order(ticker_binance, 'market', 'buy', abs(sell_Amt), None, params))

                            # 주문 취소해줘야 매도 됨
                            # myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                            sell_Amt_upbit = float(Before_amt_upbit[ticker_upbit][Situation_index - 1])
                            print(myUpbit.SellCoinMarket(upbit, ticker_upbit, abs(sell_Amt_upbit)))

                            time.sleep(0.1)

                            # 체결했으니까 내역 업데이트 해서 받아오기// 리밋 주문 새로 넣어주기
                            upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                            time.sleep(0.1)
                            balance_upbit = upbit.get_balances()
                            just_bought_amt = upbit.get_balance(ticker_upbit) - sum(Before_amt_upbit[ticker_upbit])
                            if just_bought_amt == 0:
                                print(binanceX.create_order(ticker_binance, 'market', 'sell', abs(sell_Amt), None, params))
                                Trade_infor['general'][0] = 0
                                with open(Trade_infor_path, 'w') as outfile:
                                    json.dump(Trade_infor, outfile)
                                continue

                            balance_binanace = binanceX.fetch_balance(params={"type": "future",'adjustForTimeDifference': True})
                            PNL = 0
                            for posi in balance_binanace['info']['positions']:
                                if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                                    print(posi)
                                    amt_s = float(posi['positionAmt'])
                                    entryPrice_s = float(posi['entryPrice'])
                                    leverage = float(posi['leverage'])
                                    isolated = posi['isolated']
                                    PNL = float(posi['unrealizedProfit'])
                                    break

                            for upbit_asset in balance_upbit:
                                if upbit_asset['currency'] == 'KRW':
                                    upbit_remain_money = float(upbit_asset['balance'])
                                else:
                                    continue

                            # stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * Stop_price_percent
                            # stop_price_upbit = stop_price_binance * won_rate * 0.98
                            # time.sleep(0.1)
                            # myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)
                            #
                            # myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                            # coin_volume = upbit.get_balance(ticker_upbit)
                            # myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                            # coin_net = (now_price_upbit-myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit))*Before_amt_upbit[ticker_upbit][Situation_index-1]/sum(Before_amt_upbit[ticker_upbit])+\
                            #            won_rate*(entryPrice_s-now_price_binance)*Before_amt[ticker_upbit][Situation_index-1]/sum(Before_amt[ticker_upbit])
                            # coin_net_withCommision = round((coin_net-Before_amt_upbit[ticker_upbit][Situation_index-1]*now_price_upbit*0.05/100*2)/10000,2)

                            total_asset = str(round((float(balance_binanace['BUSD']['total']) * won_rate + myUpbit.GetTotalRealMoney(balance_upbit)) / 10000, 1))

                            ## 이거 절대 김프 할 때 쓰던 건데 필요 없어서 지움
                            # Temp_won_rate = Trade_infor[ticker_upbit][0]
                            # del Trade_infor[ticker_upbit]
                            # with open(Trade_infor_path, 'w') as outfile:
                            #     json.dump(Trade_infor, outfile)
                            # earned_money_num = Krate_close-Krate_total[ticker_upbit][Situation_index-1]
                            # earned_money_den = 0.000000001
                            # for xxx in range(Situation_index):
                            #     earned_money_den += Krate_close-Krate_total[ticker_upbit][xxx]

                            # upbit_invested_money*(Before_amt[ticker_upbit][Situation_index-1]/sum(Before_amt[ticker_upbit])) -> 해당 amt의 투자 금액
                            # earned_money = (upbit_invested_money*(Before_amt[ticker_upbit][Situation_index-1]/sum(Before_amt[ticker_upbit]))*(Krate_close-Krate_total[ticker_upbit][Situation_index-1])/100 \
                            #                -upbit_invested_money*2*commission*(Before_amt[ticker_upbit][Situation_index-1]/sum(Before_amt[ticker_upbit])))/10000
                            # earned_money = (earned_money_num / earned_money_den) * (unrealizedProfit * won_rate + upbit_diff - upbit_invested_money * 2 * commission) / 10000
                            # earned_money = (unrealizedProfit*won_rate-upbit_invested_money*binance_commission+upbit_diff-upbit_invested_money*upbit_commission)*Before_amt[ticker_upbit][Situation_index-1]/sum(Before_amt[ticker_upbit])/10000
                            line_alert.SendMessage_SP("[\U0001F3B6매도] : " + str(ticker_upbit[4:]) + " 김프 " + str(round(Krate_close, 2)) + "% " + " 김프차 " + str(round(Krate_close - Krate_total[ticker_upbit][Situation_index - 1], 2)) + "% \n"
                                                      + "\n[번돈] : " + str(round(now_profit/10000, 4)) + "万 " + "[자산] : " + total_asset + "万"
                                                      + "\n[환율] : " + str(round(won_rate, 4)) + "₩"+ " [진입 환율] : " + str(round(dollar_rate[ticker_upbit][Situation_index - 1],2)) + "₩")
                            line_alert.SendMessage_Trading(str(ticker_upbit) + " BUSD KRW : " + str(won_rate) + " 시장가 : " + str(now_price_upbit) + "원 " + str(now_price_binance) + "$ " + "\n김프 계산 가격 : " + str(upbit_order_standard_close) + ' ' + str(upbit_order_standard_close)
                                                           + "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))

                            Month_profit.append(round(now_profit/10000, 4))
                            with open(Month_profit_type_file_path, 'w') as outfile:
                                json.dump(Month_profit, outfile)

                            # Situation_flag[ticker_upbit] = [False,False,False,False,False]
                            # 매도하는 여기서 해당 딕셔너리를 그냥 제거하면 될 듯. 어차피 로직의 시작은 매도인데, 매도하면 새로 반영 되니까
                            Situation_flag[ticker_upbit][Situation_index - 1] = False
                            with open(Situation_flag_type_file_path, 'w') as outfile:
                                json.dump(Situation_flag, outfile)

                            # Krate_total[ticker_upbit] = [2,2,2,2,2]
                            # 매도하는 여기서 해당 딕셔너리를 그냥 제거하면 될 듯. 어차피 로직의 시작은 매도인데, 매도하면 새로 반영 되니까
                            Krate_total[ticker_upbit][Situation_index - 1] = False
                            with open(Krate_total_type_file_path, 'w') as outfile:
                                json.dump(Krate_total, outfile)

                            Before_amt[ticker_upbit][Situation_index - 1] = False
                            with open(Before_amt_path, 'w') as outfile:
                                json.dump(Before_amt, outfile)

                            Before_amt_upbit[ticker_upbit][Situation_index - 1] = False
                            with open(Before_amt_upbit_path, 'w') as outfile:
                                json.dump(Before_amt_upbit, outfile)

                            Before_price[ticker_upbit][Situation_index - 1] = False
                            with open(Before_price_path, 'w') as outfile:
                                json.dump(Before_price, outfile)

                            Before_price_upbit[ticker_upbit][Situation_index - 1] = False
                            with open(Before_price_upbit_path, 'w') as outfile:
                                json.dump(Before_price_upbit, outfile)

                            dollar_rate[ticker_upbit][Situation_index - 1] = False
                            with open(dollar_rate_path, 'w') as outfile:
                                json.dump(dollar_rate, outfile)

                    # 물타기
                    #
                    elif ((Krate < Kimp_crit and Krate_total[ticker_upbit][Situation_index - 1] - Krate >= Krate_interval and Situation_flag[ticker_upbit][Situation_index] == False and dollar_rate[ticker_upbit][Situation_index - 1] >=won_rate)\
                            or (Krate < Kimp_crit and Krate_total[ticker_upbit][Situation_index - 1] - Krate >= Krate_interval_2 and Situation_flag[ticker_upbit][Situation_index] == False and dollar_rate[ticker_upbit][Situation_index - 1] < won_rate))\
                            and won_rate <= Trade_infor['general'][2] + won_rate_margin:

                        # and (Krate-Krate_total[ticker_upbit][0])/2.2>= profit_rate:
                        minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                        GetInMoney = Trade_infor[ticker_upbit][2]
                        Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, AD_weight_list[Situation_index] * GetInMoney / now_price_binance * set_leverage))

                        ADMoney = Buy_Amt * upbit_order_standard

                        # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                        if ADMoney < 5000:
                            ADMoney = 5000

                        # 최소 주문 수량보다 작다면 이렇게 셋팅!
                        if Buy_Amt < minimun_amount:
                            Buy_Amt = minimun_amount

                        # won_rate = myUpbit.upbit_get_usd_krw()
                        url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                        binance_order_index = 0
                        binance_order_Nsum = 0
                        for price_i, num_i in binance_orderbook_data['bids']:
                            binance_order_Nsum += float(num_i)

                            if binance_order_Nsum > abs(Buy_Amt):
                                break
                            binance_order_index += 1  # 버퍼로 하나 더해줌
                        binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                        # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                        orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                        upbit_order_index = 0
                        upbit_order_Nsum = 0

                        for upbit_order_data in orderbook_upbit['orderbook_units']:
                            upbit_order_Nsum += upbit_order_data['ask_size']

                            if upbit_order_Nsum > abs(Buy_Amt):
                                break
                            upbit_order_index += 1
                        upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                        ADMoney = Buy_Amt * upbit_order_standard
                        # 다시 정의 할 필요 없어서 지움
                        # Krate = ((upbit_order_standard / (binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
                        Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100

                        if Krate < Kimp_crit and Krate_total[ticker_upbit][Situation_index - 1] - Krate >= Krate_interval and Situation_flag[ticker_upbit][Situation_index] == False:
                            params = {'positionSide': 'SHORT'}

                            # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                            # 담보 이용해서 더 넣을 수 있게 -> free, 있는 BUSD만 쓰고 싶으면 total -used로
                            if Buy_Amt * now_price_binance / set_leverage < float(balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                                # if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['BUSD']['total']-balance_binanace['BUSD']['used']) and ADMoney < upbit_remain_money:
                                print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                                print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                                upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                                time.sleep(0.1)
                                balance_upbit = upbit.get_balances()
                                just_bought_amt = upbit.get_balance(ticker_upbit) - sum(Before_amt_upbit[ticker_upbit])
                                if just_bought_amt == 0:
                                    print(binanceX.create_order(ticker_binance, 'market', 'buy', abs(Buy_Amt), None, params))
                                    Trade_infor['general'][0] = 0
                                    with open(Trade_infor_path, 'w') as outfile:
                                        json.dump(Trade_infor, outfile)
                                    continue
                            else:
                                line_alert.SendMessage_SP("[돈 부족] : " + str(ticker_upbit[4:]) + " [김프 %] : " + str(round(Krate, 2)) + "%\n"+ "[입금 필요액] : " + str(round((ADMoney-upbit_remain_money)/10000, 2)) + "万")
                                continue

                            time.sleep(0.1)

                            # 체결했으니까 내역 업데이트 해서 받아오기
                            balance_binanace = binanceX.fetch_balance(params={"type": "future",'adjustForTimeDifference': True})

                            for posi in balance_binanace['info']['positions']:
                                if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                                    print(posi)
                                    amt_s = float(posi['positionAmt'])
                                    entryPrice_s = float(posi['entryPrice'])
                                    leverage = float(posi['leverage'])
                                    isolated = posi['isolated']
                                    break
                            for upbit_asset in balance_upbit:
                                if upbit_asset['currency'] == 'KRW':
                                    upbit_remain_money = float(upbit_asset['balance'])
                                else:
                                    continue

                            # Cross로 하니 더이상 청산 위험이 없어짐
                            # stop_price_binance = entryPrice_s * (1+1/set_leverage)*Stop_price_percent
                            # stop_price_upbit =stop_price_binance*won_rate*0.98
                            # time.sleep(0.1)
                            # myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)
                            #
                            # myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                            # coin_volume = upbit.get_balance(ticker_upbit)
                            # myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                            Situation_index = Situation_flag[ticker_upbit].index(False)

                            Situation_flag[ticker_upbit][Situation_index] = True
                            with open(Situation_flag_type_file_path, 'w') as outfile:
                                json.dump(Situation_flag, outfile)

                            Krate_total[ticker_upbit][Situation_index] = Krate
                            with open(Krate_total_type_file_path, 'w') as outfile:
                                json.dump(Krate_total, outfile)

                            Before_amt[ticker_upbit][Situation_index] = Buy_Amt
                            with open(Before_amt_path, 'w') as outfile:
                                json.dump(Before_amt, outfile)

                            just_bought_amt = upbit.get_balance(ticker_upbit) - sum(Before_amt_upbit[ticker_upbit])
                            Before_amt_upbit[ticker_upbit][Situation_index] = just_bought_amt
                            with open(Before_amt_upbit_path, 'w') as outfile:
                                json.dump(Before_amt_upbit, outfile)

                            Before_price[ticker_upbit][Situation_index] = binance_order_standard
                            with open(Before_price_path, 'w') as outfile:
                                json.dump(Before_price, outfile)

                            Before_price_upbit[ticker_upbit][Situation_index] = upbit_order_standard
                            with open(Before_price_upbit_path, 'w') as outfile:
                                json.dump(Before_price_upbit, outfile)

                            dollar_rate[ticker_upbit][Situation_index] = won_rate
                            with open(dollar_rate_path, 'w') as outfile:
                                json.dump(dollar_rate, outfile)

                            line_alert.SendMessage_SP("[\U0001F30A" + str(Situation_index) + "단계 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard / 10000, 1)) + "만원 " + "김프 : " + str(round(Krate, 2))
                                                      + "\n환율 : " + str(round(won_rate, 4)) + " 업빗가격 : " + str(round(upbit_order_standard / 10000, 4)) + "万 바낸가격 : " + str(round(binance_order_standard, 4)))
                            line_alert.SendMessage_Trading(str(ticker_upbit) + " BUSD KRW : " + str(won_rate) + " 시장가 : " + str(now_price_upbit) + str(now_price_binance) + "\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                                                           + "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))

                        else:
                            continue
            # 아직 김프 포지션 못 잡은 상태
            else:
                # 김프가 전날 기준보다 어느정도 낮아야 사게 만들었네.
                # if Krate < Kimp_crit and len(Kimplist) < CoinCnt and Krate < Krate_ExClose[ticker_upbit] - Krate_interval_getin:
                if Krate < Kimp_crit and len(Kimplist) < CoinCnt and won_rate <= Trade_infor['general'][2]:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    print("--- Target_Coin_Ticker:", ticker_binance, " minimun_amount : ", minimun_amount)
                    print(balance_binanace['BUSD'])
                    print("Total Money:", float(balance_binanace['BUSD']['total']))
                    print("Remain Money:", float(balance_binanace['BUSD']['total'] - balance_binanace['BUSD']['used']))

                    # if Kimp_crit - Krate_interval <= Krate < Kimp_crit:
                    #     get_in_cnt = 6
                    #     GetInMoney = float(balance_binanace['BUSD']['total']) / len(Kimp_target_coin) / get_in_cnt / avoid_liquid_ratio
                    # elif Kimp_crit - Krate_interval * 2 <= Krate < Kimp_crit - Krate_interval:
                    #     get_in_cnt = 5
                    #     GetInMoney = float(balance_binanace['BUSD']['total']) / len(Kimp_target_coin) / get_in_cnt / avoid_liquid_ratio
                    # elif Kimp_crit - Krate_interval * 3 <= Krate < Kimp_crit - Krate_interval * 2:
                    #     get_in_cnt = 4
                    #     GetInMoney = float(balance_binanace['BUSD']['total']) / len(Kimp_target_coin) / get_in_cnt / avoid_liquid_ratio
                    # elif Kimp_crit - Krate_interval * 4 <= Krate < Kimp_crit - Krate_interval * 3:
                    #     get_in_cnt = 3
                    #     GetInMoney = float(balance_binanace['BUSD']['total']) / len(Kimp_target_coin) / get_in_cnt / avoid_liquid_ratio
                    # elif Kimp_crit - Krate_interval * 5 <= Krate < Kimp_crit - Krate_interval * 4:
                    #     get_in_cnt = 2
                    #     GetInMoney = float(balance_binanace['BUSD']['total']) / len(Kimp_target_coin) / get_in_cnt / avoid_liquid_ratio
                    # else:
                    #     get_in_cnt = 1
                    #     GetInMoney = float(balance_binanace['BUSD']['total']) / len(Kimp_target_coin) / get_in_cnt / avoid_liquid_ratio
                    get_in_cnt = 4

                    # GetInMoney = float(balance_binanace['BUSD']['total']) / len(Kimp_target_coin) / get_in_cnt / avoid_liquid_ratio
                    GetInMoney = 666

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney / now_price_binance * set_leverage))
                    print("Buy_Amt", Buy_Amt)

                    FirstEnterMoney = Buy_Amt * upbit_order_standard

                    # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                    if FirstEnterMoney < 5000:
                        FirstEnterMoney = 5000

                    # 최소 주문 수량보다 작다면 이렇게 셋팅!
                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    # 숏 포지션을 잡습니다.
                    params = {'positionSide': 'SHORT'}

                    # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                    # if Buy_Amt * now_price_binance/set_leverage < float(balance_binanace['BUSD']['total']-balance_binanace['BUSD']['used']) and FirstEnterMoney < upbit_remain_money:
                    if Buy_Amt * now_price_binance / set_leverage < float(balance_binanace['BUSD']['free']) and FirstEnterMoney < upbit_remain_money:

                        url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                        binance_order_index = 0
                        binance_order_Nsum = 0
                        for price_i, num_i in binance_orderbook_data['bids']:
                            binance_order_Nsum += float(num_i)

                            if binance_order_Nsum > abs(Buy_Amt):
                                break
                            binance_order_index += 1  # 버퍼로 하나 더해줌
                        binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                        # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                        orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                        upbit_order_index = 0
                        upbit_order_Nsum = 0

                        for upbit_order_data in orderbook_upbit['orderbook_units']:
                            upbit_order_Nsum += upbit_order_data['ask_size']

                            if upbit_order_Nsum > abs(Buy_Amt):
                                break
                            upbit_order_index += 1
                        upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                        ADMoney = Buy_Amt * upbit_order_standard
                        Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100

                        if Krate < Kimp_crit and len(Kimplist) < CoinCnt:

                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, FirstEnterMoney))
                            upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                            time.sleep(0.1)
                            balance_upbit = upbit.get_balances()

                            Before_amt_upbit[ticker_upbit] = [False, False, False, False, False, False, False, False, False]
                            with open(Before_amt_upbit_path, 'w') as outfile:
                                json.dump(Before_amt_upbit, outfile)
                            time.sleep(0.1)

                            just_bought_amt = upbit.get_balance(ticker_upbit) - sum(Before_amt_upbit[ticker_upbit])
                            if just_bought_amt == 0:
                                print(binanceX.create_order(ticker_binance, 'market', 'buy', abs(Buy_Amt), None, params))
                                Trade_infor['general'][0] = 0
                                with open(Trade_infor_path, 'w') as outfile:
                                    json.dump(Trade_infor, outfile)
                                continue
                        else:
                            line_alert.SendMessage_SP("[돈 부족] : " + str(ticker_upbit[4:]) + " [김프 %] : " + str(round(Krate, 2)) + "%\n"+ "[필요액] : " + str(round(ADMoney/10000, 2)) + "万")
                            continue

                        time.sleep(0.1)

                        # 체결했으니까 내역 업데이트 해서 받아오기
                        balance_binanace = binanceX.fetch_balance(params={"type": "future",'adjustForTimeDifference': True})

                        for posi in balance_binanace['info']['positions']:
                            if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                                print(posi)
                                amt_s = float(posi['positionAmt'])
                                entryPrice_s = float(posi['entryPrice'])
                                leverage = float(posi['leverage'])
                                isolated = posi['isolated']
                                break

                        for upbit_asset in balance_upbit:
                            if upbit_asset['currency'] == 'KRW':
                                upbit_remain_money = float(upbit_asset['balance'])
                            else:
                                continue

                        # stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * Stop_price_percent
                        # stop_price_upbit = stop_price_binance*won_rate*0.98
                        # time.sleep(0.1)
                        # myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)
                        #
                        # myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        # time.sleep(0.1)
                        # coin_volume = upbit.get_balance(ticker_upbit)
                        # time.sleep(0.1)
                        # myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                        Kimplist.append(ticker_upbit)
                        # 파일에 리스트를 저장합니다
                        with open(Kimplist_type_file_path, 'w') as outfile:
                            json.dump(Kimplist, outfile)
                        time.sleep(0.1)

                        Situation_flag[ticker_upbit] = [True, False, False, False, False, False, False, False, False]
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)
                        time.sleep(0.1)

                        Krate_total[ticker_upbit] = [Krate, False, False, False, False, False, False, False, False]
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)
                        time.sleep(0.1)

                        Before_amt[ticker_upbit] = [Buy_Amt, False, False, False, False, False, False, False, False]
                        with open(Before_amt_path, 'w') as outfile:
                            json.dump(Before_amt, outfile)
                        time.sleep(0.1)

                        num_coin = upbit.get_balance(ticker_upbit)
                        Before_amt_upbit[ticker_upbit] = [num_coin, False, False, False, False, False, False, False, False]
                        with open(Before_amt_upbit_path, 'w') as outfile:
                            json.dump(Before_amt_upbit, outfile)
                        time.sleep(0.1)

                        Before_price[ticker_upbit] = [binance_order_standard, False, False, False, False, False, False, False, False]
                        with open(Before_price_path, 'w') as outfile:
                            json.dump(Before_price, outfile)
                        time.sleep(0.1)

                        Before_price_upbit[ticker_upbit] = [upbit_order_standard, False, False, False, False, False, False, False, False]
                        with open(Before_price_upbit_path, 'w') as outfile:
                            json.dump(Before_price_upbit, outfile)
                        time.sleep(0.1)

                        dollar_rate[ticker_upbit] = [won_rate, False, False, False, False, False, False, False, False]
                        with open(dollar_rate_path, 'w') as outfile:
                            json.dump(dollar_rate, outfile)
                        time.sleep(0.1)

                        # Trade_infor[ticker_upbit][1] = 0 여기서 0의 의미는 스탑로스 회피를 위한 물타기의 경우임
                        # Trade_infor[ticker_upbit] = [won_rate, 0, None, None, None, None, None, None, None, None, None, None]
                        # with open(Trade_infor_path, 'w') as outfile:
                        #     json.dump(Trade_infor, outfile)
                        # time.sleep(0.1)

                        Trade_infor[ticker_upbit] = [won_rate, 0, GetInMoney, False, False, False, False, False, False, False, False, False]
                        with open(Trade_infor_path, 'w') as outfile:
                            json.dump(Trade_infor, outfile)
                        time.sleep(0.1)

                        line_alert.SendMessage_SP("[\U0001F4CA진입] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard / 10000, 1)) + "만원 " + "김프 : " + str(round(Krate, 2))
                                                  + "\n환율 : " + str(round(won_rate, 4)) + " 업빗가격 : " + str(round(upbit_order_standard / 10000, 4)) + "万 바낸가격 : " + str(round(binance_order_standard, 4)))
                        line_alert.SendMessage_Trading(str(ticker_upbit) + " BUSD KRW : " + str(won_rate) + " 시장가 : " + str(now_price_upbit) + ' ' + str(now_price_binance) + "\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                                                       + "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))

                    else:
                        continue

    except Exception as e:

        # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        if str(e)[-4:] == 'BUSD' or type(e) == IndexError or Trade_infor['general'][0]==str(e):
            pass
        else:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            err = traceback.format_exc()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            line_alert.SendMessage_Trading('[에러 김프 1] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))
            # line_alert.SendMessage_SP('[에러] : \n' + str(err))
            # line_alert.SendMessage_SP('[파일] : ' + str(fname))
            # line_alert.SendMessage_SP('[라인 넘버] : ' + str(exc_tb.tb_lineno))
            # line_alert.SendMessage_Trading(str(binance_order_index) + ' ' + str(binance_order_index_close))
            # line_alert.SendMessage_Trading(str(binance_orderbook_data) + ' ' + str(binance_order_Nsum_close) + ' ' + str(amt_s))

        Trade_infor['general'][0] = str(e)
        with open(Trade_infor_path, 'w') as outfile:
            json.dump(Trade_infor, outfile)
        time.sleep(0.1)

    try:

        time.sleep(0.1)
        balance_binanace = binanceX.fetch_balance(params={"type": "future", 'adjustForTimeDifference': True})

        time.sleep(0.1)
        # 수익화 or 진입, 물타기 할 수 있고, 코드가 다 돌았는지 확인하기 위해 분단위 로그 코드를 맨 아래로 내림
        total_asset = str(round((float(balance_binanace['BUSD']['total']) * won_rate + myUpbit.GetTotalRealMoney(balance_upbit)) / 10000, 1))

        Binance_URP = 0
        for posi in balance_binanace['info']['positions']:
            if float(posi['unrealizedProfit']) != 0 and posi['symbol'][-4:] != 'USDT':
                Binance_URP += float(posi['unrealizedProfit'])

        # Summary에 차액 구하는 구간임, 근데 여기는 won_rate로 계산하는 거라서 Log에 있는 차액들의 sum이랑은 다를 수 있음.
        total_difference = str(round((myUpbit.GetTotalRealMoney(balance_upbit) - upbit_diff_BTC - myUpbit.GetTotalMoney(balance_upbit) + won_rate * Binance_URP) / 10000, 2))

        if len(Telegram_Log) != 0 and min_flag == 1:
            current_time = datetime.now(timezone('Asia/Seoul'))
            KR_time = str(current_time)
            KR_time_sliced = KR_time[:23]
            Telegram_Log_str = str()
            num_type = 0
            for key, value in Telegram_Log.items():
                num_type = num_type + 1
                key_ticker = key.replace('KRW-', '')
                Telegram_Log_str += str(num_type) + "." + key_ticker + " ↗" + str(value[0]) + " ↙" + str(value[8]) + " 물: " + str(value[3]) + " ⚠: " + str(value[7])\
                                    + "\n TGp: " + str(value[2]) + " 末p: " + str(value[9])  + " 均p: " + str(value[1]) + "\n (바: " + str(value[4]) + " 업: " + str(value[5]) + ")→" + str(value[6]) + "万\n " \
                                    + "末실현시 : " + str(value[10]) + "万" + " 末 TG: " + str(value[11]) + "万" + "\n\n"
            line_alert.SendMessage_Log("\U0001F4CA" + KR_time_sliced + "\U0001F4CA  \n" + Telegram_Log_str)

        if min_flag == 1:
            # Telegram_lev_Binanace_won = str(round((float(balance_binanace['BUSD']['total']-balance_binanace['BUSD']['used']) * set_leverage * won_rate) / 10000, 1)) + "만원"
            Telegram_lev_Binanace_won = str(round((float(balance_binanace['BUSD']['free']) * set_leverage * won_rate) / 10000, 1)) + "만원"
            Telegram_Summary = "바낸 잔액 : " + str(round(float(balance_binanace['BUSD']['total'] - balance_binanace['BUSD']['used']), 1)) + "$  " + "업빗 잔액 : " + str(round(float(upbit_remain_money / 10000), 1)) + "만원 "
            line_alert.SendMessage_Summary1minute("\U0001F4CA자산(今㉥) : " + total_asset + "万 " + "차익(今㉥) : " + total_difference + "万 \n" + "\U0001F4B5환율 : $ " + str(round(won_rate,4)) + "\n\U0001F4E6"
                                                  + Telegram_Summary + " \n\U0001F4E6" + "레버리지 고려 바낸 투자 가능액 : " + Telegram_lev_Binanace_won + " \n" + "\U0001F4B0월 실현 수익 : " + str(round(sum(Month_profit), 2)) + "万")
    except Exception as e:
        if Trade_infor['general'][1] == str(e):
            pass
        else:
            # 텔레그램 api 오류 5초 이상 쉬어줘야해서 설정
            time.sleep(5.5)
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            exc_type, exc_obj, exc_tb = sys.exc_info()
            err = traceback.format_exc()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            line_alert.SendMessage_Trading('[에러 김프 2] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))
            # line_alert.SendMessage_SP('[에러 김프 2] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))

            Trade_infor['general'][1] = str(e)
            with open(Trade_infor_path, 'w') as outfile:
                json.dump(Trade_infor, outfile)
            time.sleep(0.1)
