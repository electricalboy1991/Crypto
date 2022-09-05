#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert #라인 메세지를 보내기 위함!

import ccxt
import requests
import myBinance
import json

Kimplist_type_file_path = "/var/Autobot_seoul/Kimplist.json"
Situation_flag_type_file_path = "/var/Autobot_seoul/Situation_flag.json"
Krate_ExClose_type_file_path = "/var/Autobot_seoul/Krate_ExClose.json"
Krate_total_type_file_path = "/var/Autobot_seoul/Krate_total.json"
top_file_path = "/var/Autobot_seoul/TopCoinList.json"

# Kimplist_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Kimplist.json"
# Situation_flag_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Situation_flag.json"
# Krate_ExClose_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Krate_ExClose.json"
# Krate_total_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Krate_total.json"
# top_file_path = "C:\\Users\world\PycharmProjects\Crypto\TopCoinList.json"


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

TopCoinList = list()

#파일을 읽어서 리스트를 만듭니다.
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

Invest_Rate = 0.5
set_leverage = 3
profit_rate = 1.5
Krate_interval = 0.4
Kimp_crit = 1.9

####이거 나중에 갯수 늘려야지.. 지금은 일단 5개로 test

####이거 늘릴 때, 최소 금액 맞춰주기
CoinCnt = 10.0

# binance 객체 생성
binanceX = ccxt.binance(config={
    'apiKey': Binance_AccessKey,
    'secret': Binance_ScretKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

#잔고 데이타 가져오기
balance_binanace = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)

#내가 가진 잔고 데이터를 다 가져온다.
balance_upbit = upbit.get_balances()

won_rate = myUpbit.upbit_get_usd_krw()

upbit_remain_money=0
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

for ticker_upbit in TopCoinList:

    try:
        time.sleep(0.05)
        now_price_upbit = pyupbit.get_current_price(ticker_upbit)
    except Exception as e:
        # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        print(" Json Error " + str(ticker_upbit))
        continue

    if now_price_upbit < 10:
        continue
    ticker_temp = ticker_upbit.replace('KRW-','')
    ticker_binance = ticker_temp+'/USDT'
    ticker_binance_orderbook = ticker_temp+'USDT'

    try:
        now_price_binance = myBinance.GetCoinNowPrice(binanceX, ticker_binance)
        # Krate = ((now_price_upbit / (now_price_binance * won_rate)) - 1) * 100

        url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

        binance_orderbook_data = requests.get(url).json()
        binance_order_standard = float(binance_orderbook_data['bids'][1][0])

        orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
        upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']

        Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100

        #매수 Krate의 평균을 구하기 위한 code
        if ticker_upbit in Krate_total:
            Krate_list = list(filter(None, Krate_total[ticker_upbit]))
            Krate_average = sum(Krate_list)/len(Krate_list)
        else:
            # Krate_total[ticker_upbit] = [2,2,2,2,2]
            # Krate_list = list(filter(None, Krate_total[ticker_upbit]))
            Krate_average = 20


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
                    profit_rate = 2.1
                elif 0<Krate_average<=1:
                    profit_rate = 1.5
                elif 1<Krate_average<=2:
                    profit_rate = 1.2
                elif 2 < Krate_average <= 2.5:
                    profit_rate = 1.1
                else:
                    profit_rate = 1.0


                #수익화  // 수익화 절대 기준은 매번 좀 보고 바꿔줘야되나,,,,
                if Krate > 0.5 \
                        and Krate > Krate_ExClose[ticker_upbit]+0.1 \
                        and Krate - Krate_average > profit_rate:
                    isolated = True  # 격리모드인지

                    Target_Coin_Symbol = ticker_binance.replace("/", "")

                    leverage = 0  # 레버리지

                    # 숏잔고
                    for posi in balance_binanace['info']['positions']:
                        if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                            print(posi)
                            amt_s = float(posi['positionAmt'])
                            entryPrice_s = float(posi['entryPrice'])
                            leverage = float(posi['leverage'])
                            isolated = posi['isolated']
                            break

                    # 거래 지점이랑 맞닿게 하기 위해 수익화 조건 한번 더 돌림
                    won_rate = myUpbit.upbit_get_usd_krw()

                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                    binance_orderbook_data = requests.get(url).json()
                    binance_order_standard = float(binance_orderbook_data['bids'][1][0])

                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']

                    Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
                    if Krate > 0.5 \
                            and Krate > Krate_ExClose[ticker_upbit] + 0.1 \
                            and Krate - Krate_average > profit_rate:
                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        params = {'positionSide': 'SHORT'}
                        binanceX.cancel_all_orders(ticker_binance)
                        # print(binanceX.create_order(ticker_binance, 'limit', 'buy', abs(amt_s), now_price_binance, params))
                        print(binanceX.create_order(ticker_binance, 'market', 'buy', abs(amt_s), None, params))

                        #주문 취소해줘야 매도 됨
                        myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                        time.sleep(0.1)
                        print(myUpbit.SellCoinMarket(upbit, ticker_upbit,upbit.get_balance(ticker_upbit)))

                        time.sleep(0.1)

                        line_alert.SendMessage("[김프 수익] : " + str(ticker_upbit) + " 김프" + str(round(Krate,2)) + "% " + " 김프 차이" + str(round(Krate - Krate_average,2)) + "% ")
                        total_asset = str(round((float(balance_binanace['USDT']['total']) * won_rate + myUpbit.GetTotalRealMoney(balance_upbit)) / 10000, 1))
                        line_alert.SendMessage("[자산] : " + total_asset + "만원")

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
                    else:
                        continue

                #물타기 1회
                elif Krate <Kimp_crit \
                        and Krate_total[ticker_upbit][0]-Krate >= Krate_interval\
                        and Situation_flag[ticker_upbit][1] == False:
                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, myBinance.GetAmount(float(balance_binanace['USDT']['total']),
                        now_price_binance, Invest_Rate / CoinCnt))) * set_leverage

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, Buy_Amt))

                    ADMoney = Buy_Amt * upbit_order_standard

                    # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                    if ADMoney < 5000:
                        ADMoney = 5000

                    # 최소 주문 수량보다 작다면 이렇게 셋팅!
                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    won_rate = myUpbit.upbit_get_usd_krw()
                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                    binance_orderbook_data = requests.get(url).json()
                    binance_order_standard = float(binance_orderbook_data['bids'][1][0])

                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']
                    Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
                    if Krate < 2 and Krate_total[ticker_upbit][0]-Krate >= Krate_interval\
                            and Situation_flag[ticker_upbit][1] == False:
                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['USDT']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            continue

                        time.sleep(0.1)
                        line_alert.SendMessage("[김프 1단계 물] : " + str(ticker_upbit) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))

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

                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*0.98
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*0.98

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
                    else:
                        continue
                # 물타기 2회
                elif Krate < Kimp_crit \
                        and Krate_total[ticker_upbit][1] - Krate >= Krate_interval \
                        and Situation_flag[ticker_upbit][2] == False:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, myBinance.GetAmount(
                        float(balance_binanace['USDT']['total']),now_price_binance, Invest_Rate / CoinCnt))) * set_leverage

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, Buy_Amt))

                    ADMoney = Buy_Amt * upbit_order_standard

                    # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                    if ADMoney < 5000:
                        ADMoney = 5000

                    # 최소 주문 수량보다 작다면 이렇게 셋팅!
                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    won_rate = myUpbit.upbit_get_usd_krw()
                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                    binance_orderbook_data = requests.get(url).json()
                    binance_order_standard = float(binance_orderbook_data['bids'][1][0])

                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']
                    Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
                    if Krate < Kimp_crit \
                            and Krate_total[ticker_upbit][1] - Krate >= Krate_interval \
                            and Situation_flag[ticker_upbit][2] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['USDT']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            continue

                        time.sleep(0.1)
                        line_alert.SendMessage("[김프 2단계 물] : " + str(ticker_upbit) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))

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

                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*0.98
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*0.98

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
                    else:
                        continue
                # 물타기 3회
                elif Krate < Kimp_crit \
                        and Krate_total[ticker_upbit][2] - Krate >= Krate_interval \
                        and Situation_flag[ticker_upbit][3] == False:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, myBinance.GetAmount(
                        float(balance_binanace['USDT']['total']),
                        now_price_binance, Invest_Rate / CoinCnt))) * set_leverage

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, Buy_Amt))

                    ADMoney = Buy_Amt * upbit_order_standard

                    # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                    if ADMoney < 5000:
                        ADMoney = 5000

                    # 최소 주문 수량보다 작다면 이렇게 셋팅!
                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    won_rate = myUpbit.upbit_get_usd_krw()
                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                    binance_orderbook_data = requests.get(url).json()
                    binance_order_standard = float(binance_orderbook_data['bids'][1][0])

                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']
                    Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
                    if Krate < 2 \
                        and Krate_total[ticker_upbit][2] - Krate >= Krate_interval \
                        and Situation_flag[ticker_upbit][3] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['USDT']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            continue

                        time.sleep(0.1)
                        line_alert.SendMessage(
                            "[김프 3단계 물] : " + str(ticker_upbit) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))

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

                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*0.98
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*0.98

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
                    else:
                        continue
                # 물타기 4회
                elif Krate < Kimp_crit \
                        and Krate_total[ticker_upbit][3] - Krate >= Krate_interval \
                        and Situation_flag[ticker_upbit][4] == False:

                    minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, myBinance.GetAmount(
                        float(balance_binanace['USDT']['total']),
                        now_price_binance, Invest_Rate / CoinCnt))) * set_leverage

                    Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, Buy_Amt))

                    ADMoney = Buy_Amt * upbit_order_standard

                    # 5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
                    if ADMoney < 5000:
                        ADMoney = 5000

                    # 최소 주문 수량보다 작다면 이렇게 셋팅!
                    if Buy_Amt < minimun_amount:
                        Buy_Amt = minimun_amount

                    won_rate = myUpbit.upbit_get_usd_krw()
                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                    binance_orderbook_data = requests.get(url).json()
                    binance_order_standard = float(binance_orderbook_data['bids'][1][0])

                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']
                    Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100
                    if Krate < 2 \
                            and Krate_total[ticker_upbit][3] - Krate >= Krate_interval \
                            and Situation_flag[ticker_upbit][4] == False:

                        params = {'positionSide': 'SHORT'}

                        # data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                        if Buy_Amt*now_price_binance/set_leverage < float(balance_binanace['USDT']['free']) and ADMoney < upbit_remain_money:
                            print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                            print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, ADMoney))
                        else:
                            continue

                        time.sleep(0.1)
                        line_alert.SendMessage(
                            "[김프 4단계 물] : " + str(ticker_upbit) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 "+"김프 : "+ str(round(Krate,2)))

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

                        stop_price_binance = entryPrice_s * (1+1/set_leverage)*0.98
                        stop_price_upbit =myUpbit.GetAvgBuyPrice(balance_upbit,ticker_upbit)*(1+1/set_leverage)*0.98

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
                    else:
                        continue
        # 아직 김프 포지션 못 잡은 상태
        else:
            if Krate < Kimp_crit and len(Kimplist) < CoinCnt \
                    and Krate < Krate_ExClose[ticker_upbit] - Krate_interval:

                minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker_binance)

                print("--- Target_Coin_Ticker:", ticker_binance, " minimun_amount : ", minimun_amount)
                print(balance_binanace['USDT'])
                print("Total Money:", float(balance_binanace['USDT']['total']))
                print("Remain Money:", float(balance_binanace['USDT']['free']))

                Buy_Amt = float(binanceX.amount_to_precision(ticker_binance,myBinance.GetAmount(float(balance_binanace['USDT']['total']),
                          now_price_binance, Invest_Rate / CoinCnt))) * set_leverage

                Buy_Amt = float(binanceX.amount_to_precision(ticker_binance, Buy_Amt))
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
                if Buy_Amt * now_price_binance/set_leverage < float(balance_binanace['USDT']['free']) and FirstEnterMoney < upbit_remain_money:

                    won_rate = myUpbit.upbit_get_usd_krw()
                    url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'

                    binance_orderbook_data = requests.get(url).json()
                    binance_order_standard = float(binance_orderbook_data['bids'][1][0])

                    orderbook_upbit = pyupbit.get_orderbook(ticker_upbit)
                    upbit_order_standard = orderbook_upbit['orderbook_units'][1]['ask_price']
                    Krate = ((upbit_order_standard / (binance_order_standard * won_rate)) - 1) * 100

                    if Krate < 2 and len(Kimplist) < CoinCnt\
                        and Krate < Krate_ExClose[ticker_upbit] - Krate_interval:

                        print(binanceX.create_order(ticker_binance, 'market', 'sell', Buy_Amt, None, params))
                        print(myUpbit.BuyCoinMarket(upbit, ticker_upbit, FirstEnterMoney))
                        time.sleep(0.1)
                    else:
                        continue
                else:
                    continue
                # stop_price_binance = now_price_binance*1.3
                # stop_price_upbit = now_price_upbit*1.3
                #
                # myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)
                #
                # coin_volume = upbit.get_balance(ticker_upbit)
                # myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                time.sleep(0.1)
                line_alert.SendMessage(
                    "[김프 진입] : " + str(ticker_upbit) + " " + str(round(Buy_Amt * upbit_order_standard/10000, 1)) + "만원 " +"김프 : "+ str(round(Krate,2)))

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

                stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * 0.98
                stop_price_upbit = myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) * (1 + 1 / set_leverage) * 0.98

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

                Situation_flag[ticker_upbit] = [True,False,False,False,False]
                with open(Situation_flag_type_file_path, 'w') as outfile:
                    json.dump(Situation_flag, outfile)
                time.sleep(0.1)

                Krate_total[ticker_upbit] = [Krate,None,None,None,None]
                with open(Krate_total_type_file_path, 'w') as outfile:
                    json.dump(Krate_total, outfile)

            else:
                continue

    except Exception as e:
        # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        print("There is no " + str(ticker_binance) + ' in BINANCE FUTURES')
