#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit
import sys, os
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert #라인 메세지를 보내기 위함!
import traceback
import ccxt
import requests
import myBinance
import json
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup as bs

Kimplist_type_file_path = "/var/Autobot_seoul/Kimplist.json"
Situation_flag_type_file_path = "/var/Autobot_seoul/Situation_flag.json"
Krate_ExClose_type_file_path = "/var/Autobot_seoul/Krate_ExClose.json"
Krate_total_type_file_path = "/var/Autobot_seoul/Krate_total.json"
top_file_path = "/var/Autobot_seoul/TopCoinList.json"
Trade_infor_path = "/var/Autobot_seoul/Trade_infor.json"

# Kimplist_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Kimplist.json"
# Situation_flag_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Situation_flag.json"
# Krate_ExClose_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Krate_ExClose.json"
# Krate_total_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Krate_total.json"
# top_file_path = "C:\\Users\world\PycharmProjects\Crypto\TopCoinList.json"
# Trade_infor_path = "C:\\Users\world\PycharmProjects\Crypto\Trade_infor.json"

page_USDT = requests.get("https://coinmarketcap.com/ko/currencies/tether/")
soup_USDT = bs(page_USDT.text, "html.parser")
str_TetherKRW = soup_USDT.select_one('div.priceValue span').get_text()
TetherKRW=float(str_TetherKRW[1]+str_TetherKRW[3:9])

page_BUSD = requests.get("https://coinmarketcap.com/ko/currencies/binance-usd/")
soup_BUSD = bs(page_BUSD.text, "html.parser")
str_BUSDKRW = soup_BUSD.select_one('div.priceValue span').get_text()
BUSDKRW=float(str_BUSDKRW[1]+str_BUSDKRW[3:9])

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)

time.sleep(0.05)

#시간 정보를 가져옵니다. 아침 9시의 경우 서버에서는 hour변수가 0이 됩니다.
time_info = time.gmtime()
hour = time_info.tm_hour
min = time_info.tm_min

#한국시간 9시 -> 0
hour_crit = 20
min_crit = 25
print(hour, min)

#빈 리스트를 선언합니다.
Kimplist = list()

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(Kimplist_type_file_path, 'r', encoding="utf-8") as json_file:
        Kimplist = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First 1")

Situation_flag = dict()

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(Situation_flag_type_file_path, 'r', encoding="utf-8") as json_file:
        Situation_flag = json.load(json_file)
except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First 2")

Krate_ExClose= dict()

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(Krate_ExClose_type_file_path, 'r', encoding="utf-8") as json_file:
        Krate_ExClose = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First 3")

Krate_total = dict()

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(Krate_total_type_file_path, 'r', encoding="utf-8") as json_file:
        Krate_total = json.load(json_file)
except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First 4")

Trade_infor = dict()

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(Trade_infor_path, 'r', encoding="utf-8") as json_file:
        Trade_infor = json.load(json_file)
except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First 5")

TopCoinList = list()
Telegram_Log = dict()

try:
    with open(top_file_path, "r", encoding="utf-8") as json_file:
        TopCoinList = json.load(json_file)
        if hour ==hour_crit and min % 60 ==min_crit and len(Kimplist)==0:
            TopCoinList = myUpbit.GetTopCoinList("day", 30)

            setForExclose = set(Krate_ExClose.keys())
            setForTotal = set(Krate_total.keys())
            setForFlag = set(Situation_flag.keys())
            setForTopcoin = set(TopCoinList)

            setDifference_Exclose = list(setForExclose.difference(setForTopcoin))
            setDifference_Total = list(setForTotal.difference(setForTopcoin))
            setDifference_Flag  = list(setForTotal.difference(setForFlag))

            for remove_element_Exclose in setDifference_Exclose:
                if remove_element_Exclose in Krate_ExClose:
                    del Krate_ExClose[remove_element_Exclose]

            for remove_element_Total in setDifference_Total:
                if remove_element_Total in Krate_total:
                    del Krate_total[remove_element_Total]

            for remove_element_Flag in setDifference_Flag:
                if remove_element_Flag in Situation_flag:
                    del Situation_flag[remove_element_Flag]

            with open(top_file_path, 'w', encoding="utf-8") as outfile:
                json.dump(TopCoinList, outfile)
            with open(Krate_ExClose_type_file_path, 'w') as outfile:
                json.dump(Krate_ExClose, outfile)
            with open(Krate_total_type_file_path, 'w') as outfile:
                json.dump(Krate_total, outfile)
            with open(Situation_flag_type_file_path, 'w') as outfile:
                json.dump(Situation_flag, outfile)

except Exception as e:
    TopCoinList = myUpbit.GetTopCoinList("day",30)
    print("Exception by First")

Invest_Rate = 0.21
set_leverage = 3
profit_rate_criteria = 1.5
Krate_interval = 0.35
AD_criteria = 95
Kimp_crit = 1.5
Stop_price_percent = 0.97
close_criteria = 1.1
GetInMoney=250
Binance_commission = 0.0003

####이거 나중에 갯수 늘려야지.. 지금은 일단 5개로 test

####이거 늘릴 때, 최소 금액 맞춰주기
CoinCnt = 10.0

# binance 객체 생성
binanceX = ccxt.binance(config={'apiKey': Binance_AccessKey,'secret': Binance_ScretKey,'enableRateLimit': True,'options': {'defaultType': 'future'}})

#잔고 데이타 가져오기
# balance_binanace = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)

#내가 가진 잔고 데이터를 다 가져온다.
balance_upbit = upbit.get_balances()
upbit_diff_BTC = float(myUpbit.NumOfTickerCoin(balance_upbit, "KRW-BTC")) * (pyupbit.get_current_price("KRW-BTC") - float(myUpbit.GetAvgBuyPrice(balance_upbit, "KRW-BTC")))

won_rate = myUpbit.upbit_get_usd_krw()

upbit_remain_money=0

for jj in Kimplist:
    if not myUpbit.IsHasCoin(balance_upbit, jj):
        del Krate_ExClose[jj]
        del Krate_total[jj]
        del Situation_flag[jj]
        Kimplist.remove(jj)

        with open(Krate_ExClose_type_file_path, 'w') as outfile:
            json.dump(Krate_ExClose, outfile)
        with open(Krate_total_type_file_path, 'w') as outfile:
            json.dump(Krate_total, outfile)
        with open(Situation_flag_type_file_path, 'w') as outfile:
            json.dump(Situation_flag, outfile)
        with open(Kimplist_type_file_path, 'w') as outfile:
            json.dump(Kimplist, outfile)


for upbit_asset in balance_upbit:
    if upbit_asset['currency'] == 'KRW':
        upbit_remain_money = float(upbit_asset['balance'])
    else:
        continue

characters = "KRW-"

try:
    TopCoinList.remove("KRW-BTC")
except Exception as e:
    print("BTC remove error", e)


#거래 순서를 김프 평단이 낮은 애부터 거래 되도록 하기 위함...
if len(Krate_total) !=0:

    Krate_aver_total = dict()
    Traded_sorted_list = list()

    for temp_ticker in Krate_total:
        temp_Krate_dummy=Krate_total[temp_ticker]
        while -100 in temp_Krate_dummy:
            temp_Krate_dummy.remove(-100)
        Krate_average = sum(temp_Krate_dummy) / len(temp_Krate_dummy)
        Krate_aver_total[temp_ticker] = Krate_average

    Traded_list = sorted(Krate_aver_total.items(), key = lambda item: item[1])
    #평단 높은 애 먼저 물타고 싶으면 아래 주석을 푼다.
    #Traded_list = sorted(Krate_aver_total.items(), key=lambda item: item[1], reverse = True)
    for ii in Traded_list:
        Traded_sorted_list.append(ii[0])

    s = set(Traded_sorted_list)
    Rest_topcoin = [x for x in TopCoinList if x not in s]

    Sorted_topcoinlist = Traded_sorted_list+Rest_topcoin

else:
    Sorted_topcoinlist=TopCoinList

for ticker_upbit in Sorted_topcoinlist:

    time.sleep(0.1)
    now_price_upbit = pyupbit.get_current_price(ticker_upbit)

    if now_price_upbit < 10 and myUpbit.CheckCoinInList(Kimplist,ticker_upbit) == False:
        continue
    ticker_temp = ticker_upbit.replace('KRW-','')
    ticker_binance = ticker_temp+'/BUSD'
    ticker_binance_orderbook = ticker_temp+'BUSD'

    try:
        time.sleep(0.05)
        now_price_binance = myBinance.GetCoinNowPrice(binanceX, ticker_binance)
        # Krate = ((now_price_upbit / (now_price_binance * won_rate)) - 1) * 100

        Target_Coin_Symbol = ticker_binance.replace("/", "")

        balance_binanace = binanceX.fetch_balance(params={"type": "future"})
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
        Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))

        #바이낸스 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
        binance_order_index = 0
        binance_order_Nsum = 0
        for price_i, num_i in binance_orderbook_data['bids']:
            binance_order_Nsum +=float(num_i)
            binance_order_index += 1 #버퍼로 하나 더해줌
            if binance_order_Nsum > abs(Buy_Amt):
                break
        binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

        # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
        time.sleep(0.05)
        orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
        time.sleep(0.05)
        upbit_order_index = 0
        upbit_order_Nsum = 0

        for upbit_order_data in orderbook_upbit['orderbook_units']:
            upbit_order_Nsum += upbit_order_data['ask_size']
            upbit_order_index +=1
            if upbit_order_Nsum > abs(Buy_Amt):
                break
        upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

        # 바이낸스에서 팔 때 슬리피지는 다르게 해줘야지
        binance_order_index_close = 0
        binance_order_Nsum_close = 0
        for price_i, num_i in binance_orderbook_data['asks']:
            binance_order_Nsum_close += float(num_i)
            binance_order_index_close += 1  # 버퍼로 하나 더해줌
            if binance_order_Nsum_close > abs(amt_s):
                break
        binance_order_standard_close = float(binance_orderbook_data['asks'][binance_order_index_close][0])

        # 업비트에서 팔 때 슬리피지는 다르게 해줘야지
        upbit_order_index_close = 0
        upbit_order_Nsum_close = 0

        for upbit_order_data in orderbook_upbit['orderbook_units']:
            upbit_order_Nsum_close += upbit_order_data['bid_size']
            upbit_order_index_close += 1
            if upbit_order_Nsum_close > abs(amt_s):
                break
        upbit_order_standard_close = orderbook_upbit['orderbook_units'][upbit_order_index_close]['bid_price']

        ADMoney = Buy_Amt * upbit_order_standard

        if ticker_upbit in Kimplist:
            Krate = ((upbit_order_standard / (binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
            Krate_close = ((upbit_order_standard_close / (binance_order_standard_close * Trade_infor[ticker_upbit][0])) - 1) * 100
        else:
            Krate = ((upbit_order_standard / (binance_order_standard * BUSDKRW)) - 1) * 100
        """
        if myUpbit.IsHasCoin(balance_upbit,ticker_upbit):
            profit_rate = 100 * ((upbit_order_standard - myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)) * myUpbit.NumOfTickerCoin(
                balance_upbit, ticker_upbit) - BUSDKRW * amt_s * (entryPrice_s - binance_order_standard)) / (myUpbit.NumOfTickerCoin(balance_upbit, ticker_upbit) 
                * myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) - amt_s * entryPrice_s * BUSDKRW)
        """

        #매수 Krate의 평균을 구하기 위한 code
        if ticker_upbit in Krate_total:
            temp_Krate_dummy2 = Krate_total[ticker_upbit]
            while -100 in temp_Krate_dummy2:
                temp_Krate_dummy2.remove(-100)
                Krate_average = sum(temp_Krate_dummy2) / len(temp_Krate_dummy2)
            TryNumber = len(temp_Krate_dummy2)
        else:
            # Krate_total[ticker_upbit] = [2,2,2,2,2]
            # Krate_list = list(filter(None, Krate_total[ticker_upbit]))
            Krate_average = 20

        #위에서 Krate_total -100 다 remove시켜서 다시 가지고 옴
        with open(Krate_total_type_file_path, 'r', encoding="utf-8") as json_file:
            Krate_total = json.load(json_file)

        #TopCoinList가 바뀌어서 ExClose에 새로 넣어줘야할 때
        if ticker_upbit in Krate_ExClose:
            pass
        else:
            Krate_ExClose[ticker_upbit] = Krate
            with open(Krate_ExClose_type_file_path, 'w') as outfile:
                json.dump(Krate_ExClose, outfile)

        # 종가를 저장하는 로직
        if hour == hour_crit and min % 60 ==min_crit:
                Krate_ExClose[ticker_upbit] = Krate
                with open(Krate_ExClose_type_file_path, 'w') as outfile:
                    json.dump(Krate_ExClose, outfile)

        leverage = 0  # 레버리지
        isolated = False  # 격리모드인지

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

        #################################################################################################################
        # 격리 모드로 설정
        if isolated == False:
            try:
                print(binanceX.fapiPrivate_post_margintype(
                    {'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
            except Exception as e:
                print("Exception:", e)
        #################################################################################################################


        # 전략에 의해 매수 했고

        if myUpbit.CheckCoinInList(Kimplist,ticker_upbit) == True:
            # 따라서 잔고도 있다.
            if myUpbit.IsHasCoin(balance_upbit, ticker_upbit) == True:

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

                upbit_diff = float(myUpbit.NumOfTickerCoin(balance_upbit,ticker_upbit)) * (upbit_order_standard_close-float(myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)))

                warning_price_binance = entryPrice_s * (1 + 1 / set_leverage) * 0.95
                warning_percent=round((now_price_binance-entryPrice_s)/(warning_price_binance-entryPrice_s)*100,1)
                if warning_percent<0:
                    warning_percent = 0.0

                Telegram_Log[ticker_upbit] = [round(Krate_close,2),round(Krate_average,1),round(Krate_average+profit_rate_criteria,2),TryNumber-1,
                                              round(unrealizedProfit*(1-Binance_commission)*BUSDKRW/10000,1),round(upbit_diff/10000,1),round((unrealizedProfit*(1-Binance_commission)*BUSDKRW+upbit_diff)/10000,1), warning_percent,round(Krate,2)]

                #수익화  // 수익화 절대 기준은 매번 좀 보고 바꿔줘야되나,,,,
                upbit_invested_money=myUpbit.GetCoinNowMoney(balance_upbit, ticker_upbit)
                if (Krate_close > close_criteria and Krate_close > Krate_ExClose[ticker_upbit]+0.1 and Krate_close - Krate_average > profit_rate_criteria) or (unrealizedProfit*(1-Binance_commission)*BUSDKRW+upbit_diff)>upbit_invested_money*profit_rate_criteria/100:
                        # and Krate - Krate_average <= profit_rate*2.2:
                    isolated = True  # 격리모드인지

                    leverage = 0  # 레버리지

                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'
                    binance_orderbook_data = requests.get(url).json()
                    # 바이낸스에서 팔 때 슬리피지는 다르게 해줘야지
                    binance_order_index_close = 0
                    binance_order_Nsum_close = 0
                    for price_i, num_i in binance_orderbook_data['asks']:
                        binance_order_Nsum_close += float(num_i)
                        binance_order_index_close += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum_close > abs(amt_s):
                            break
                    binance_order_standard_close = float(binance_orderbook_data['asks'][binance_order_index_close][0])

                    # 업비트에서 팔 때 슬리피지는 다르게 해줘야지
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index_close = 0
                    upbit_order_Nsum_close = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum_close += upbit_order_data['bid_size']
                        upbit_order_index_close += 1
                        if upbit_order_Nsum_close > abs(amt_s):
                            break
                    upbit_order_standard_close = orderbook_upbit['orderbook_units'][upbit_order_index_close]['bid_price']

                    # 다시 정의 할 필요 없어서 지움
                    Krate_close = ((upbit_order_standard_close / (binance_order_standard_close * Trade_infor[ticker_upbit][0])) - 1) * 100

                    if (Krate_close > close_criteria and Krate_close > Krate_ExClose[ticker_upbit]+0.1 and Krate_close - Krate_average > profit_rate_criteria) or (unrealizedProfit*(1-Binance_commission)*BUSDKRW+upbit_diff)>upbit_invested_money*profit_rate_criteria/100:
                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        params = {'positionSide': 'SHORT'}
                        binanceX.cancel_all_orders(ticker_binance)
                        # print(binanceX.create_order(ticker_binance, 'limit', 'buy', abs(amt_s), now_price_binance, params))
                        print(binanceX.create_order(ticker_binance, 'market', 'buy', abs(amt_s), None, params))

                        #주문 취소해줘야 매도 됨
                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        time.sleep(0.1)
                        num_coin=upbit.get_balance(ticker_upbit)
                        print(myUpbit.SellCoinMarket(upbit, ticker_upbit,upbit.get_balance(ticker_upbit)))

                        time.sleep(0.1)


                        coin_net = (now_price_upbit-myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit))*num_coin+BUSDKRW*(entryPrice_s-now_price_binance)*abs(amt_s)
                        coin_net_withCommision = round((coin_net-num_coin*now_price_upbit*0.05/100*2)/10000,2)

                        total_asset = str(round((float(balance_binanace['BUSD']['total']) * BUSDKRW + myUpbit.GetTotalRealMoney(balance_upbit)) / 10000, 1))

                        Kimplist.remove(ticker_upbit)
                        # 파일에 리스트를 저장합니다
                        with open(Kimplist_type_file_path, 'w') as outfile:
                            json.dump(Kimplist, outfile)

                        # Situation_flag[ticker_upbit] = [False,False,False,False,False]
                        #매도하는 여기서 해당 딕셔너리를 그냥 제거하면 될 듯. 어차피 로직의 시작은 매도인데, 매도하면 새로 반영 되니까
                        del Situation_flag[ticker_upbit]
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)

                        # Krate_total[ticker_upbit] = [2,2,2,2,2]
                        #매도하는 여기서 해당 딕셔너리를 그냥 제거하면 될 듯. 어차피 로직의 시작은 매도인데, 매도하면 새로 반영 되니까
                        del Krate_total[ticker_upbit]
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)


                        Temp_won_rate = Trade_infor[ticker_upbit][0]
                        del Trade_infor[ticker_upbit]
                        with open(Trade_infor_path, 'w') as outfile:
                            json.dump(Trade_infor, outfile)

                        line_alert.SendMessage_SP("[매도] : " + str(ticker_upbit[4:]) + " 김프 " + str(round(Krate_close,2)) + "% " + " 김프차 " + str(round(Krate_close - Krate_average,2)) + "% \n"
                                                    +"[바낸 Profit] : " + str(round(unrealizedProfit*Temp_won_rate/10000,2)) + "万("+str(round(unrealizedProfit,2))+"$)\n" + "[업빗 Profit] : " + str(round(upbit_diff/10000,2))+ "万"
                                                  +"\n[번돈] : " + str(coin_net_withCommision) + "万 " + "[자산] : " + total_asset + "万")
                        line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+ " 시장가 : " + str(now_price_upbit) + str(now_price_binance) +"\n김프 계산 가격 : " + str(upbit_order_standard_close) + ' ' + str(upbit_order_standard_close)
                                                  +"\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))


                    else:
                        continue

                #청산 회피를 위한 물타기
                elif warning_percent>AD_criteria and Trade_infor[ticker_upbit][1] == 0:
                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)
                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))

                    ADMoney = Buy_Amt * upbit_order_standard

                    # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                    if ADMoney < 5000:
                        ADMoney = 5000

                    # 최소 주문 수량보다 작다면 이렇게 셋팅!
                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    # binance_orderbook_data = requests.get(url).json()
                    # binance_order_standard = float(binance_orderbook_data['bids'][1][0])
                    #
                    # orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    # upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']

                    params = {'positionSide': 'SHORT'}

                    # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                    if Buy_Amt * now_price_binance / set_leverage < float(balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                        print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                        print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                    else:
                        continue

                    time.sleep(0.1)

                    # 체결했으니까 내역 업데이트 해서 받아오기
                    balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                    upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                    time.sleep(0.1)
                    balance_upbit = upbit.get_balances()

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

                    stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * Stop_price_percent
                    stop_price_upbit = myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) * (1 + 1 / set_leverage) * Stop_price_percent

                    myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                    myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                    coin_volume = upbit.get_balance(ticker_upbit)
                    myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                    ADMoney_index=Situation_flag[ticker_upbit].index(False)


                    Situation_flag[ticker_upbit][ADMoney_index] = True
                    with open(Situation_flag_type_file_path, 'w') as outfile:
                        json.dump(Situation_flag, outfile)

                    Krate_total[ticker_upbit][ADMoney_index] = Krate
                    with open(Krate_total_type_file_path, 'w') as outfile:
                        json.dump(Krate_total, outfile)

                    #물을 탔다는 의미임
                    Trade_infor[ticker_upbit][1] = 1
                    with open(Trade_infor_path, 'w') as outfile:
                        json.dump(Trade_infor, outfile)
                    time.sleep(0.1)

                    line_alert.SendMessage_SP("[청산 경고 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard / 10000, 1)) + "만원 " + "김프 : " + str(round(Krate, 2)))
                    line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) + "\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)+
                        "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))

                #물타기 1회
                elif Krate <Kimp_crit and Krate_total[ticker_upbit][0]-Krate >= Krate_interval and Situation_flag[ticker_upbit][1] == False:
                        # and (Krate-Krate_total[ticker_upbit][0])/2.2>= profit_rate:
                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))

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
                        binance_order_index += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum > abs(Buy_Amt):
                            break
                    binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                    # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index = 0
                    upbit_order_Nsum = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum += upbit_order_data['ask_size']
                        upbit_order_index += 1
                        if upbit_order_Nsum > abs(Buy_Amt):
                            break
                    upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                    ADMoney = Buy_Amt * upbit_order_standard
                        # 다시 정의 할 필요 없어서 지움
                    Krate = ((upbit_order_standard / (binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100

                    if Krate < 2 and Krate_total[ticker_upbit][0]-Krate >= Krate_interval\
                            and Situation_flag[ticker_upbit][1] == False:
                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            line_alert.SendMessage_SP('돈 없어서 물 못탐')
                            continue

                        time.sleep(0.1)

                        # 체결했으니까 내역 업데이트 해서 받아오기
                        balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                        upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                        time.sleep(0.1)
                        balance_upbit = upbit.get_balances()

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


                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*Stop_price_percent
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*Stop_price_percent

                        myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        coin_volume = upbit.get_balance(ticker_upbit)
                        myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                        Situation_flag[ticker_upbit][1] = True
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)

                        Krate_total[ticker_upbit][1] = Krate
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)

                        line_alert.SendMessage_SP("[1단계 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))
                        line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) +"\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                                                  +"\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))

                    else:
                        continue
                # 물타기 2회
                elif Krate < Kimp_crit and Krate_total[ticker_upbit][1] - Krate >= Krate_interval and Situation_flag[ticker_upbit][2] == False:
                        # and (Krate-Krate_total[ticker_upbit][0])/2.2>= profit_rate:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))

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
                        binance_order_index += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum > abs(Buy_Amt):
                            break
                    binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                    # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index = 0
                    upbit_order_Nsum = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum += upbit_order_data['ask_size']
                        upbit_order_index += 1
                        if upbit_order_Nsum > abs(Buy_Amt):
                            break
                    upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                    ADMoney = Buy_Amt * upbit_order_standard

                        # 다시 정의 할 필요 없어서 지움
                    Krate = ((upbit_order_standard / (binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
                    if Krate < Kimp_crit \
                            and Krate_total[ticker_upbit][1] - Krate >= Krate_interval \
                            and Situation_flag[ticker_upbit][2] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            line_alert.SendMessage_SP('돈 없어서 물 못탐')
                            continue

                        time.sleep(0.1)

                        # 체결했으니까 내역 업데이트 해서 받아오기
                        balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                        upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                        time.sleep(0.1)
                        balance_upbit = upbit.get_balances()

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

                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*Stop_price_percent
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*Stop_price_percent

                        myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        coin_volume = upbit.get_balance(ticker_upbit)
                        myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)


                        Situation_flag[ticker_upbit][2] = True
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)

                        Krate_total[ticker_upbit][2] = Krate
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)

                        line_alert.SendMessage_SP("[2단계 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))
                        line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) +"\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                                                  +"\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))
                    else:
                        continue
                # 물타기 3회
                elif Krate < Kimp_crit and Krate_total[ticker_upbit][2] - Krate >= Krate_interval and Situation_flag[ticker_upbit][3] == False:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))

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
                        binance_order_index += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum > abs(Buy_Amt):
                            break
                    binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                    # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index = 0
                    upbit_order_Nsum = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum += upbit_order_data['ask_size']
                        upbit_order_index += 1
                        if upbit_order_Nsum > abs(Buy_Amt):
                            break
                    upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                    ADMoney = Buy_Amt * upbit_order_standard

                        # 다시 정의 할 필요 없어서 지움
                    Krate = ((upbit_order_standard / (binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
                    if Krate < 2 \
                        and Krate_total[ticker_upbit][2] - Krate >= Krate_interval \
                        and Situation_flag[ticker_upbit][3] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            line_alert.SendMessage_SP('돈 없어서 물 못탐')
                            continue

                        time.sleep(0.1)

                        # 체결했으니까 내역 업데이트 해서 받아오기
                        balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                        upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                        time.sleep(0.1)
                        balance_upbit = upbit.get_balances()

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

                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*Stop_price_percent
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*Stop_price_percent

                        myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        coin_volume = upbit.get_balance(ticker_upbit)
                        myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)


                        Situation_flag[ticker_upbit][3] = True
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)

                        Krate_total[ticker_upbit][3] = Krate
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)

                        line_alert.SendMessage_SP("[3단계 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))
                        line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) +"\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                                                  +"\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))
                    else:
                        continue
                # 물타기 4회
                elif Krate < Kimp_crit and Krate_total[ticker_upbit][3] - Krate >= Krate_interval and Situation_flag[ticker_upbit][4] == False:
                        # and (Krate-Krate_total[ticker_upbit][0])/2.2>= profit_rate:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))
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
                        binance_order_index += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum > abs(Buy_Amt):
                            break
                    binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                    # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index = 0
                    upbit_order_Nsum = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum += upbit_order_data['ask_size']
                        upbit_order_index += 1
                        if upbit_order_Nsum > abs(Buy_Amt):
                            break
                    upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                    ADMoney = Buy_Amt * upbit_order_standard
                    Krate = ((upbit_order_standard / (binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
                    if Krate < 2 \
                            and Krate_total[ticker_upbit][3] - Krate >= Krate_interval \
                            and Situation_flag[ticker_upbit][4] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            line_alert.SendMessage_SP('돈 없어서 물 못탐')
                            continue

                        time.sleep(0.1)

                        # 체결했으니까 내역 업데이트 해서 받아오기
                        balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                        upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                        time.sleep(0.1)
                        balance_upbit = upbit.get_balances()

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

                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*Stop_price_percent
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*Stop_price_percent

                        myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        coin_volume = upbit.get_balance(ticker_upbit)
                        myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                        Situation_flag[ticker_upbit][4] = True
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)

                        Krate_total[ticker_upbit][4] = Krate
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)

                        line_alert.SendMessage_SP("[4단계 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))
                        line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) +"\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                                                  +"\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))
                    else:
                        continue

                        # 물타기 5회
                elif Krate < Kimp_crit and Krate_total[ticker_upbit][4] - Krate >= Krate_interval and Situation_flag[ticker_upbit][5] == False:
                        # and (Krate-Krate_total[ticker_upbit][0])/2.2>= profit_rate:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))

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
                        binance_order_index += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum > abs(Buy_Amt):
                            break
                    binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                    # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index = 0
                    upbit_order_Nsum = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum += upbit_order_data['ask_size']
                        upbit_order_index += 1
                        if upbit_order_Nsum > abs(Buy_Amt):
                            break
                    upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                    ADMoney = Buy_Amt * upbit_order_standard
                    Krate = ((upbit_order_standard / (
                                binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
                    if Krate < 2 \
                            and Krate_total[ticker_upbit][4] - Krate >= Krate_interval \
                            and Situation_flag[ticker_upbit][5] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt * now_price_binance / set_leverage < float(
                                balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            line_alert.SendMessage_SP('돈 없어서 물 못탐')
                            continue

                        time.sleep(0.1)

                        # 체결했으니까 내역 업데이트 해서 받아오기
                        balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                        upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                        time.sleep(0.1)
                        balance_upbit = upbit.get_balances()

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

                        stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * Stop_price_percent
                        stop_price_upbit = myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) * (
                                    1 + 1 / set_leverage) * Stop_price_percent

                        myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        coin_volume = upbit.get_balance(ticker_upbit)
                        myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                        Situation_flag[ticker_upbit][5] = True
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)

                        Krate_total[ticker_upbit][5] = Krate
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)

                        line_alert.SendMessage_SP("[5단계 물] : " + str(ticker_upbit[4:]) + " " + str(
                            round(Buy_Amt * upbit_order_standard / 10000, 1)) + "만원 " + "김프 : " + str(
                            round(Krate, 2)))
                        line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) + "\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                            + "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))
                    else:
                        continue

                #물타기 6회
                elif Krate < Kimp_crit and Krate_total[ticker_upbit][5] - Krate >= Krate_interval and Situation_flag[ticker_upbit][6] == False:
                        # and (Krate-Krate_total[ticker_upbit][0])/2.2>= profit_rate:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))

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
                        binance_order_index += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum > abs(Buy_Amt):
                            break
                    binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                    # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index = 0
                    upbit_order_Nsum = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum += upbit_order_data['ask_size']
                        upbit_order_index += 1
                        if upbit_order_Nsum > abs(Buy_Amt):
                            break
                    upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                    ADMoney = Buy_Amt * upbit_order_standard
                    Krate = ((upbit_order_standard / (
                                binance_order_standard * Trade_infor[ticker_upbit][0])) - 1) * 100
                    if Krate < 2 \
                            and Krate_total[ticker_upbit][5] - Krate >= Krate_interval \
                            and Situation_flag[ticker_upbit][6] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt * now_price_binance / set_leverage < float(balance_binanace['BUSD']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            line_alert.SendMessage_SP('돈 없어서 물 못탐')
                            continue

                        time.sleep(0.1)

                        # 체결했으니까 내역 업데이트 해서 받아오기
                        balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                        upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                        time.sleep(0.1)
                        balance_upbit = upbit.get_balances()

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

                        stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * Stop_price_percent
                        stop_price_upbit = myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) * (
                                    1 + 1 / set_leverage) * Stop_price_percent

                        myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        coin_volume = upbit.get_balance(ticker_upbit)
                        myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                        Situation_flag[ticker_upbit][6] = True
                        with open(Situation_flag_type_file_path, 'w') as outfile:
                            json.dump(Situation_flag, outfile)

                        Krate_total[ticker_upbit][6] = Krate
                        with open(Krate_total_type_file_path, 'w') as outfile:
                            json.dump(Krate_total, outfile)

                        line_alert.SendMessage_SP("[6단계 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard / 10000, 1)) + "만원 " + "김프 : " + str(round(Krate, 2)))
                        line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) + "\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                            + "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))
                    else:
                        continue

                else:
                    continue
        # 아직 김프 포지션 못 잡은 상태
        else:
            if Krate < Kimp_crit and len(Kimplist) < CoinCnt and Krate < Krate_ExClose[ticker_upbit] - Krate_interval:

                minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                print("--- Target_Coin_Ticker:", ticker_binance, " minimun_amount : ", minimun_amount)
                print(balance_binanace['BUSD'])
                print("Total Money:", float(balance_binanace['BUSD']['total']))
                print("Remain Money:", float(balance_binanace['BUSD']['free']))

                Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, GetInMoney/now_price_binance*set_leverage))
                print("Buy_Amt",Buy_Amt)

                FirstEnterMoney = Buy_Amt*upbit_order_standard

                # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                if FirstEnterMoney < 5000:
                    FirstEnterMoney = 5000

                # 최소 주문 수량보다 작다면 이렇게 셋팅!
                if Buy_Amt < minimun_amount:
                    Buy_Amt = minimun_amount

                # 숏 포지션을 잡습니다.
                params = {'positionSide': 'SHORT'}

                # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                if Buy_Amt * now_price_binance/set_leverage < float(balance_binanace['BUSD']['free']) and FirstEnterMoney < upbit_remain_money:

                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                    binance_order_index = 0
                    binance_order_Nsum = 0
                    for price_i, num_i in binance_orderbook_data['bids']:
                        binance_order_Nsum += float(num_i)
                        binance_order_index += 1  # 버퍼로 하나 더해줌
                        if binance_order_Nsum > abs(Buy_Amt):
                            break
                    binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

                    # 업비트 Order북에서 슬리피지 밀리는 거 대비해서 호가창 몇번째 볼지에 대해 정하는 코드
                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_index = 0
                    upbit_order_Nsum = 0

                    for upbit_order_data in orderbook_upbit['orderbook_units']:
                        upbit_order_Nsum += upbit_order_data['ask_size']
                        upbit_order_index += 1
                        if upbit_order_Nsum > abs(Buy_Amt):
                            break
                    upbit_order_standard = orderbook_upbit['orderbook_units'][upbit_order_index]['ask_price']

                    ADMoney = Buy_Amt * upbit_order_standard
                    Krate = ((upbit_order_standard / (binance_order_standard * BUSDKRW)) - 1) * 100

                    if Krate < 2 and len(Kimplist) < CoinCnt\
                        and Krate < Krate_ExClose[ticker_upbit] - Krate_interval:

                        print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                        time.sleep(0.1)
                        print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, FirstEnterMoney))
                    else:
                        continue
                else:
                    continue
                time.sleep(0.1)

                #체결했으니까 내역 업데이트 해서 받아오기
                balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                time.sleep(0.1)
                balance_upbit = upbit.get_balances()

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

                stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * Stop_price_percent
                stop_price_upbit = myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) * (1 + 1 / set_leverage) * Stop_price_percent

                myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                time.sleep(0.1)
                coin_volume = upbit.get_balance(ticker_upbit)
                time.sleep(0.1)
                myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                Kimplist.append(ticker_upbit)
                # 파일에 리스트를 저장합니다
                with open(Kimplist_type_file_path, 'w') as outfile:
                    json.dump(Kimplist, outfile)
                time.sleep(0.1)

                Situation_flag[ticker_upbit] = [True,False,False,False,False,False,False]
                with open(Situation_flag_type_file_path, 'w') as outfile:
                    json.dump(Situation_flag, outfile)
                time.sleep(0.1)

                Krate_total[ticker_upbit] = [Krate,-100,-100,-100,-100,-100,-100]
                with open(Krate_total_type_file_path, 'w') as outfile:
                    json.dump(Krate_total, outfile)
                time.sleep(0.1)

                #Trade_infor[ticker_upbit][1] = 0 여기서 0의 의미는 스탑로스 회피를 위한 물타기의 경우임
                Trade_infor[ticker_upbit] = [BUSDKRW,0,None,None,None,None,None,None,None,None,None,None]
                with open(Trade_infor_path, 'w') as outfile:
                    json.dump(Trade_infor, outfile)
                time.sleep(0.1)


                line_alert.SendMessage_SP("[진입] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 " +"김프 : "+ str(round(Krate,2)))
                line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + ' ' + str(now_price_binance) + "\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)
                    + "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))

    except Exception as e:
        # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        print('예외가 발생했습니다.', e)
        if str(e)[-4:] == 'BUSD':
            pass
        else:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            err = traceback.format_exc()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            line_alert.SendMessage_Trading('[에러] : \n' + str(err) + '\n[파일] : '+ str(fname)+ '\n[라인 넘버] : '+ str(exc_tb.tb_lineno))
            line_alert.SendMessage_Trading(str(binance_order_index) + ' ' + str(binance_order_index_close))

time.sleep(0.1)
balance_binanace = binanceX.fetch_balance(params={"type": "future"})

time.sleep(0.1)
#수익화 or 진입, 물타기 할 수 있고, 코드가 다 돌았는지 확인하기 위해 분단위 로그 코드를 맨 아래로 내림
total_asset = str(round((float(balance_binanace['BUSD']['total']) * BUSDKRW + myUpbit.GetTotalRealMoney(balance_upbit)) / 10000, 1))

Binance_URP = 0
for posi in balance_binanace['info']['positions']:
    if float(posi['unrealizedProfit']) != 0:
        Binance_URP+=float(posi['unrealizedProfit'])

#Summary에 차액 구하는 구간임, 근데 여기는 BUSDKRW로 계산하는 거라서 Log에 있는 차액들의 sum이랑은 다를 수 있음.
total_difference=str(round((myUpbit.GetTotalRealMoney(balance_upbit)-upbit_diff_BTC-myUpbit.GetTotalMoney(balance_upbit)+BUSDKRW*Binance_URP)/10000,2))

if len(Telegram_Log) !=0:
    current_time = datetime.now(timezone('Asia/Seoul'))
    KR_time=str(current_time)
    KR_time_sliced =KR_time[:23]
    Telegram_Log_str = str()
    num_type=0
    for key, value in Telegram_Log.items():
        num_type=num_type+1
        key_ticker = key.replace('KRW-', '')
        Telegram_Log_str += str(num_type) + "." + key_ticker + " ↗" + str(value[0])+ " ↙" + str(value[8]) + " 均p: " + str(value[1]) + " TGp: " + str(value[2]) + "\n" + "물: " + str(value[3])  \
                            + " ⚠: " +str(value[7]) + "%" + " (바差: " +str(value[4]) + " 업差: " +str(value[5]) +  ")→" +str(value[6]) + "万\n\n"
    line_alert.SendMessage_Log("  ♥♥" +KR_time_sliced+"♥♥  \n"+Telegram_Log_str)

Telegram_lev_Binanace_won = str(round((float(balance_binanace['BUSD']['free']) * set_leverage * BUSDKRW) / 10000, 1)) + "만원"
Telegram_Summary = "바낸 잔액 : " + str(round(float(balance_binanace['BUSD']['free']),1))+ "$  " + "업빗 잔액 : " + str(round(float(upbit_remain_money/10000),1)) +"만원 "
line_alert.SendMessage_Summary1minute("★자산(今㉥) : " + total_asset + "万 "+"차익(今㉥) : " + total_difference +"万 \n"+"♣환율 : ㉥ " + str(BUSDKRW)+ "₩ ($ : "+ str(won_rate) + "₩)"+ "\n♥"
                                      +Telegram_Summary+" \n♠" + "레버리지 고려 바낸 투자 가능액 : " + Telegram_lev_Binanace_won)

