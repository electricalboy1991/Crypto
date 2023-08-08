import myBinance # 만든 코드
import ccxt # 주문 명령 업비트나, 바이낸스에 줄 때, 이용하는 라이브러리
import ende_key  # 암복호화키
import my_key  # 업비트 시크릿 액세스키
import json
import time
import platform
import line_alert #라인 메세지를 보내기 위함!
from datetime import datetime
from pytz import timezone
import sys, os
import traceback

# 윈도우랑 리눅스 접속 구분을 위한 코드
if platform.system() != 'Windows':
    from binance import Client
else:
    from binance.client import Client
    pass

# RSI 기준 / USER PARAMETER
RSI_criteria_0 = 34.2
RSI_criteria_1 = 29.2
RSI_criteria_2 = 24
RSI_criteria_3 = 19

profit_rate = 5

# 내가 사는 돈
RSI_criteria_0_GetInMoney = 100
RSI_criteria_1_GetInMoney = 250
RSI_criteria_2_GetInMoney = 450
RSI_criteria_3_GetInMoney = 600

min_temp = 0

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)



while True:
    try:
        # 이전 거래에 대한 정보를 저장하기 위한 경로
        if platform.system() == 'Windows':
            RSI_info_Binance_path = "C:\\Users\world\PycharmProjects\Crypto\RSI_info_Binance_sell.json"
        else:
            RSI_info_Binance_path = "/var/autobot/RSI_info_Binance_sell.json"

        RSI_info_Binance = dict()

        try:
            # 이전 매매 정보 로드
            with open(RSI_info_Binance_path, 'r', encoding="utf-8") as json_file:
                RSI_info_Binance = json.load(json_file)

        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            RSI_info_Binance["general"] = [False, False, False, False, False, False, False, False, False, False, False, False]
            RSI_info_Binance["Pre_RSI_time_0"] = float(0)
            RSI_info_Binance["Pre_RSI_time_1"] = float(0)
            RSI_info_Binance["Pre_RSI_time_2"] = float(0)
            RSI_info_Binance["Pre_RSI_time_3"] = float(0)
            RSI_info_Binance["Num_input"] = float(0)
            print("RSI 파일 없음")

        # 보수적으로 8초 쉬었다가 감
        time.sleep(8)

        # 현재 시간 불러오기
        time_info = time.gmtime()
        hour = time_info.tm_hour
        min = time_info.tm_min

        # 메시지를 1분에 1번만 오게 하기 위한 FLAG

        if min_temp == min:
            min_flag = 0
        else:
            min_flag = 1
        min_temp = min

        # 바이낸스에서 특정 기능을 하게 하기 위한 client 객체 생성
        client = Client(Binance_AccessKey, Binance_ScretKey)
        order = client.get_open_orders()
        time.sleep(0.05)
        binanceX = ccxt.binance(config={'apiKey': Binance_AccessKey, 'secret': Binance_ScretKey, 'enableRateLimit': True, 'options': {'defaultType': 'spot', 'adjustForTimeDifference': True, 'recvWindow': 15000}})

        # binance API의 서버 시간을 가져옴
        server_time = binanceX.fetch_time()
        # 로컬 컴퓨터의 시간을 가져옴
        local_time = int(time.time() * 1000)
        # 서버 시간과 로컬 시간의 차이를 계산하여 nonce 값을 설정
        nonce = max(server_time, local_time)

        response = binanceX.fetch_balance(params={'recvWindow': 15000})



        timestamp = datetime.now().timestamp()
        print(timestamp)

        Target_Coin_Ticker = 'BTC/USDT'
        # Target_Coin_Ticker = 'BTC/BUSD'
        Target_Coin_Ticker_splited, Stable_coin_type = Target_Coin_Ticker.split('/')

        # 현재 가격 받아오기
        now_price_binance = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

        # 비트코인의 140분봉(캔들) 정보를 가져온다.
        df = myBinance.GetOhlcv(binanceX, Target_Coin_Ticker, '1h')

        # rsi_hour지표를 구합니다.
        rsi_hour = float(myBinance.GetRSI(df, 14, -1))

        print("BTC_BOT_WORKING")
        print("NOW RSI:", rsi_hour)

        profit_rate_list = list()
        invested_money = list()

        # 내가 매도 가격 설정을 안해놓으니까, BTC를 사도
        for i, open_order in enumerate(order):
            profit_rate_list.append(round((now_price_binance - float(order[i]['price']) / (profit_rate/100+1)) / (float(order[i]['price']) / (profit_rate/100+1)) * 100, 2))
            invested_money.append(float(order[i]['price']) / (profit_rate/100+1) * float(order[i]['origQty']))

        current_time = datetime.now(timezone('Asia/Seoul'))
        KR_time = str(current_time)
        KR_time_sliced = KR_time[:23]
        RSI_string = "  \U0001F3C4\U0001F3C4" + KR_time_sliced + "\U0001F3C4\U0001F3C4  \n" + '[RSI_바이낸스] : ' + str(round(rsi_hour, 2)) \
                     + "\n" + '[NOW 가격] : ' + str(round(now_price_binance, 2)) + " $" + "\n"

        for j, profit_rate_i in enumerate(profit_rate_list):
            RSI_string += '[' + str(j + 1) + ". 수익%] : " + str(profit_rate_i) + " 투입 $ : " + str(round(invested_money[j], 1)) + "\n"

        # 지정가 걸어논 애들이, 매도 되면 알람 오게 함
        if RSI_info_Binance["Num_input"] > len(invested_money):

            profit_messenger = "[\U0001F3C4 RSI_바이낸스_수익화 진행 완료 알림 \U0001F3C4]"
            line_alert.SendMessage_SP(profit_messenger)

            # 갯수 새롭게 저장하기 위한 코드
            RSI_info_Binance["Num_input"] = len(invested_money)
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)


        elif RSI_info_Binance["Num_input"] == len(invested_money):
            pass

        elif RSI_info_Binance["Num_input"] < len(invested_money):
            RSI_info_Binance["Num_input"] = len(invested_money)
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)
        if min_flag == 1:
            line_alert.SendMessage_1hourRSI(RSI_string)


        if rsi_hour <= RSI_criteria_0 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_0"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_0"]) == 0)):
            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_0_GetInMoney / now_price_binance))

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            #비트코인 이제 그냥 모아가기 위해서, 매도 안함
            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance*(1+profit_rate/100),0)))
            time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_0"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_0 = "[\U0001F3C4RSI_0_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_0_GetInMoney, 2)) + '$ ' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * (1+profit_rate/100), 0))
            line_alert.SendMessage_SP(rsi_messenger_0)

        elif rsi_hour <= RSI_criteria_1 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_1"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_1"]) == 0)):
            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_1_GetInMoney / now_price_binance))

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            # 비트코인 이제 그냥 모아가기 위해서, 매도 안함
            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance*(1+profit_rate/100),0)))
            time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_1"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_1 = "[\U0001F3C4RSI_1_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_1_GetInMoney, 2)) + '$ ' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * (1+profit_rate/100), 0))
            line_alert.SendMessage_SP(rsi_messenger_1)


        elif rsi_hour <= RSI_criteria_2 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_2"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_2"]) == 0)):

            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_2_GetInMoney / now_price_binance))

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            # 비트코인 이제 그냥 모아가기 위해서, 매도 안함
            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance * (1+profit_rate/100), 0)))
            time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_2"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_2 = "[\U0001F3C4RSI_2_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_2_GetInMoney, 2)) + '$' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * (1+profit_rate/100), 0))
            line_alert.SendMessage_SP(rsi_messenger_2)

        elif rsi_hour <= RSI_criteria_3 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_3"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_3"]) == 0)):

            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_3_GetInMoney / now_price_binance))

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            # 비트코인 이제 그냥 모아가기 위해서, 매도 안함
            print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance * (1+profit_rate/100), 0)))
            time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_3"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_3 = "[\U0001F3C4RSI_3_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_3_GetInMoney, 2)) + '$' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * (1+profit_rate/100), 0))
            line_alert.SendMessage_SP(rsi_messenger_3)

    except Exception as e:
        # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        if RSI_info_Binance['general'][0] == str(e):
            pass
        else:
            #텔레그램 api 오류 5초 이상 쉬어줘야해서 설정
            time.sleep(5.5)
            print('예외가 발생했습니다.', e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            err = traceback.format_exc()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            line_alert.SendMessage_Trading('[에러 RSI] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))
            if str(e) == "binance Account has insufficient balance for requested action." :
                line_alert.SendMessage_SP("[\U0001F3C4 바이낸스] : RSI 달러 부족")

        RSI_info_Binance['general'][0] = str(e)
        with open(RSI_info_Binance_path, 'w') as outfile:
            json.dump(RSI_info_Binance, outfile)
        time.sleep(0.1)





