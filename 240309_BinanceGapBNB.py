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
import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
TOKEN = '7089325839:AAGzipLppNQbk5xCcSOV95rxg9WqyQPGREU'

# Initialize the bot token and create an Updater
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

GetInMoney = 100
getInGap = -1.1
BNB_on = 1
extraFlag =0
# Function to update variables
def update_variable(update, context):
    global BNB_on, GetInMoney, getInGap, extraFlag

    command = update.message.text.split(' ')[0]
    new_value = float(context.args[0])

    # Existing RSI criteria updates
    if command == '/b':
        BNB_on = int(new_value)
        response = f"BNB_on has been updated to {BNB_on}"
    elif command == '/gap':
        getInGap = new_value
        response = f"getInGap has been updated to {getInGap}"
    elif command == '/g':
        GetInMoney = new_value
        response = f"GetInMoney has been updated to {GetInMoney}"
    elif command == '/ex':
        extraFlag = new_value
        response = f"extraFlag has been updated to {extraFlag}"
    else:
        response = "Invalid command"

    update.message.reply_text(response)

# Register the command handler
dispatcher.add_handler(CommandHandler(['b', 'gap', 'g','ex'], update_variable))

# Start the bot
updater.start_polling()

# 윈도우랑 리눅스 접속 구분을 위한 코드
if platform.system() != 'Windows':
    from binance import Client
else:
    from binance.client import Client
    pass

min_temp = 0
Target_Coin_Ticker = 'BNB/USDT'
Target_Coin_Symbol = Target_Coin_Ticker.replace("/", "")
ticker_binance_orderbook = Target_Coin_Symbol

set_leverage =3

# 숏 포지션을 잡습니다.
params = {'positionSide': 'SHORT'}

BTCtransferAmt = 0.02 # 만약에 BNB 사는 GetInMoney의 크기가 커지면, 이거 크기도 키워줘야함
borrowedMoney = 310 # 빌리는 거니까 좀 더
nowPriceBuffer = 0.1 # 현재 시가에서 위 호가를 보기 위한 버퍼
#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)


while True:
    try:

        if platform.system() == 'Windows':
            BNB_info_Binance_path = "C:\\Users\world\PycharmProjects\Crypto\BNB_info_Binance.json"
        else:
            BNB_info_Binance_path = "/var/autobot/BNB_info_Binance.json"

        BNB_info_Binance = dict()

        try:
            # 이전 매매 정보 로드
            with open(BNB_info_Binance_path, 'r', encoding="utf-8") as json_file:
                BNB_info_Binance = json.load(json_file)

        except Exception as e:
            # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
            BNB_info_Binance["general"] = [False, False, False, False, False, False, False, False, False, False, False, False]
            BNB_info_Binance["Pre_BNB_time_0"] = float(0)
            BNB_info_Binance["Pre_BNB_time_1"] = float(0)
            BNB_info_Binance["Pre_BNB_time_2"] = float(0)
            BNB_info_Binance["Pre_BNB_time_3"] = float(0)
            BNB_info_Binance["Num_input"] = float(0)
            print("BNB 파일 없음")

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

        # 정각마다 에러 초기화 -> 돈 부족 알람 1시간에 1번은 오게 리셋
        if min == 0:
            BNB_info_Binance['general'][0] = 0
            with open(BNB_info_Binance_path, 'w') as outfile:
                json.dump(BNB_info_Binance, outfile)
            time.sleep(0.1)


        # 바이낸스에서 특정 기능을 하게 하기 위한 client 객체 생성
        client = Client(Binance_AccessKey, Binance_ScretKey)
        order = client.get_open_orders()
        time.sleep(0.05)
        binanceX = ccxt.binance(config={'apiKey': Binance_AccessKey, 'secret': Binance_ScretKey, 'enableRateLimit': True, 'options': {'defaultType': 'spot', 'adjustForTimeDifference': True, 'recvWindow': 15000}})
        time.sleep(0.1)
        response = binanceX.fetch_balance(params={'recvWindow': 15000})
        time.sleep(0.1)

        usdt_balance = response['total']['USDT']
        print("USDT Balance:", usdt_balance)


        # binance API의 서버 시간을 가져옴
        server_time = binanceX.fetch_time()
        # 로컬 컴퓨터의 시간을 가져옴
        local_time = int(time.time() * 1000)
        # 서버 시간과 로컬 시간의 차이를 계산하여 nonce 값을 설정
        nonce = max(server_time, local_time)

        response = binanceX.fetch_balance(params={'recvWindow': 15000})

        timestamp = datetime.now().timestamp()
        print(timestamp)
        print("Formatted Time 1:", timestamp)

        binanceXF = ccxt.binance(config={'apiKey': Binance_AccessKey, 'secret': Binance_ScretKey, 'enableRateLimit': True, 'options': {'defaultType': 'future', 'recvWindow': 15000}})
        balance_binanace = binanceXF.fetch_balance(params={"type": "future", 'adjustForTimeDifference': True})

        minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
        for posi in balance_binanace['info']['positions']:
            if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                print(posi)
                amt_s = float(posi['positionAmt'])
                entryPrice_s = float(posi['entryPrice'])
                leverage = float(posi['leverage'])
                isolated = posi['isolated']
                unrealizedProfit = float(posi['unrealizedProfit'])
                break


        # BNB 현물가격임
        now_price_binance = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)
        Target_Coin_Ticker_splited, Stable_coin_type = Target_Coin_Ticker.split('/')
        Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, GetInMoney / now_price_binance))

        url = 'https://fapi.binance.com/fapi/v1/depth?symbol=' + ticker_binance_orderbook + '&limit=' + '10'
        binance_orderbook_data = requests.get(url).json()

        binance_order_index = 0
        binance_order_Nsum = 0
        for price_i, num_i in binance_orderbook_data['bids']:
            binance_order_Nsum += float(num_i)

            if binance_order_Nsum > abs(Buy_Amt):
                break
            binance_order_index += 1  # 버퍼로 하나 더해줌
        binance_order_standard = float(binance_orderbook_data['bids'][binance_order_index][0])

        if now_price_binance - binance_order_standard + nowPriceBuffer < getInGap and (((timestamp - float(BNB_info_Binance["Pre_BNB_time_0"]) > 86400) or (float(BNB_info_Binance["Pre_BNB_time_0"]) == 0)) or extraFlag ==1):

            if usdt_balance / now_price_binance < Buy_Amt :
                response = client.transfer_spot_to_margin(asset='BTC', amount=BTCtransferAmt)
                time.sleep(2)
                response = client.create_margin_loan(asset='USDT', amount=borrowedMoney, collateralCoin='BTC')  # 50 USDT as an example
                time.sleep(2)
                result = client.transfer_margin_to_spot(asset='USDT', amount=borrowedMoney)
            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt+minimun_amount))
            print(binanceXF.create_order(Target_Coin_Ticker, 'market', 'sell', Buy_Amt, None, params))
            time.sleep(0.1)

            BNB_info_Binance["Pre_BNB_time_0"] = timestamp
            with open(BNB_info_Binance_path, 'w') as outfile:
                json.dump(BNB_info_Binance, outfile)
            time.sleep(0.1)

            extraFlag = 0

            BNB_messenger_0 = "[☄️BNB_구매 투입 금액] : " + str(round(GetInMoney, 2)) + '$ ' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [현 선 Gap] : ' + str(round(now_price_binance-binance_order_standard+nowPriceBuffer, 2))
            line_alert.SendMessage_SP(BNB_messenger_0)

        BNB_string = " ☄️☄️" + "BNB GAP HEDGE" + "☄️☄️\n" + '[BNB Gap On] : ' + str(round(BNB_on, 0)) + "\n" + '[잔액] : ' + str(round(usdt_balance, 1)) + '$' \
                     + "\n" + '[NOW 가격] : ' + str(round(now_price_binance, 2)) + "$" \
                     + "\n[진입 갭] : " + str(round(getInGap, 1)) \
                     + "\n[현재 갭] : " + str(round(now_price_binance - binance_order_standard+nowPriceBuffer, 1)) \
                     + "\n[1회 진입 액] : " + str(round(GetInMoney, 1)) + "$"

        if min_flag == 1:
            line_alert.SendMessage_BNB(BNB_string)
        print(now_price_binance - binance_order_standard + nowPriceBuffer)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        err = traceback.format_exc()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

        line_alert.SendMessage_Trading('[☄️에러 BNB] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))
        BNB_info_Binance['general'][0] = str(e)
        with open(BNB_info_Binance_path, 'w') as outfile:
            json.dump(BNB_info_Binance, outfile)
        time.sleep(0.1)

