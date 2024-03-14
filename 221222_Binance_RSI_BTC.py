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

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
TOKEN = '7089325839:AAGzipLppNQbk5xCcSOV95rxg9WqyQPGREU'

# Initialize the bot token and create an Updater
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Global variable
RSI_on = 1
# RSI 기준 / USER PARAMETER
RSI_criteria_0 = 34.2
RSI_criteria_1 = 29.2
RSI_criteria_2 = 24.1
RSI_criteria_3 = 19.1
# 내가 사는 돈
RSI_criteria_0_GetInMoney = 200
RSI_criteria_1_GetInMoney = 300
RSI_criteria_2_GetInMoney = 500
RSI_criteria_3_GetInMoney = 700

#20$는 마진으로 더 붙임
GetInMoneyTotal = RSI_criteria_0_GetInMoney+RSI_criteria_1_GetInMoney+RSI_criteria_2_GetInMoney+RSI_criteria_3_GetInMoney + 20


BTCtransferAmt = 0.05
# # Function to handle the /update_variable command
# def update_variable(update, context):
#     global RSI_on
#     new_value = context.args[0]
#     RSI_on = int(new_value)
#     update.message.reply_text(f"RSI1_on has been updated to {RSI_on}")
#
# # Function to handle regular messages
# def message_handler(update, context):
#     message_text = update.message.text
#     if message_text.startswith('/r1on'):
#         update_variable(update, context)
#     else:
#         update.message.reply_text("Invalid command")
#
# # Register the command and message handlers
# dispatcher.add_handler(CommandHandler('r1on', update_variable))
# dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
#
# # Start the bot
# updater.start_polling()

# Function to update variables
def update_variable(update, context):
    global RSI_on, RSI_criteria_0, RSI_criteria_1, RSI_criteria_2, RSI_criteria_3
    global RSI_criteria_0_GetInMoney, RSI_criteria_1_GetInMoney, RSI_criteria_2_GetInMoney, RSI_criteria_3_GetInMoney

    command = update.message.text.split(' ')[0]
    new_value = float(context.args[0])

    # Existing RSI criteria updates
    if command == '/ron':
        RSI_on = int(new_value)
        response = f"RSI_on has been updated to {RSI_on}"
    elif command == '/r0':
        RSI_criteria_0 = new_value
        response = f"RSI_criteria_0 has been updated to {RSI_criteria_0}"
    elif command == '/r1':
        RSI_criteria_1 = new_value
        response = f"RSI_criteria_1 has been updated to {RSI_criteria_1}"
    elif command == '/r2':
        RSI_criteria_2 = new_value
        response = f"RSI_criteria_2 has been updated to {RSI_criteria_2}"
    elif command == '/r3':
        RSI_criteria_3 = new_value
        response = f"RSI_criteria_3 has been updated to {RSI_criteria_3}"
    # New RSI GetInMoney updates
    elif command == '/g0':
        RSI_criteria_0_GetInMoney = new_value
        response = f"RSI_criteria_0_GetInMoney has been updated to {RSI_criteria_0_GetInMoney}"
    elif command == '/g1':
        RSI_criteria_1_GetInMoney = new_value
        response = f"RSI_criteria_1_GetInMoney has been updated to {RSI_criteria_1_GetInMoney}"
    elif command == '/g2':
        RSI_criteria_2_GetInMoney = new_value
        response = f"RSI_criteria_2_GetInMoney has been updated to {RSI_criteria_2_GetInMoney}"
    elif command == '/g3':
        RSI_criteria_3_GetInMoney = new_value
        response = f"RSI_criteria_3_GetInMoney has been updated to {RSI_criteria_3_GetInMoney}"
    else:
        response = "Invalid command"

    update.message.reply_text(response)

# Register the command handler
dispatcher.add_handler(CommandHandler(['ron', 'r0', 'r1', 'r2', 'r3', 'g0', 'g1', 'g2', 'g3'], update_variable))

# Start the bot
updater.start_polling()

# 윈도우랑 리눅스 접속 구분을 위한 코드
if platform.system() != 'Windows':
    from binance import Client
else:
    from binance.client import Client
    pass

profit_rate = 2

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
            RSI_info_Binance_path = "C:\\Users\world\PycharmProjects\Crypto\RSI_info_Binance.json"
        else:
            RSI_info_Binance_path = "/var/autobot/RSI_info_Binance.json"

        RSI_info_Binance = dict()
        print(RSI_on)
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
        time.sleep(5)

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
        if min ==0:
            RSI_info_Binance['general'][0] = 0
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
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

        # 내가 매도 가격 설정을 안해놓으니까, BTC를 사도  // 지금은 안 씀
        for i, open_order in enumerate(order):
            profit_rate_list.append(round((now_price_binance - float(order[i]['price']) / profit_rate) / (float(order[i]['price']) / profit_rate) * 100, 2))
            invested_money.append(float(order[i]['price']) / profit_rate * float(order[i]['origQty']))

        current_time = datetime.now(timezone('Asia/Seoul'))
        KR_time = str(current_time)
        KR_time_sliced = KR_time[:23]
        RSI_string = "  \U0001F3C2\U0001F3C2" + KR_time_sliced + "\U0001F3C2\U0001F3C2  \n" + '[RSI1_Power] : ' + str(round(RSI_on, 0))+' [잔액] : ' + str(round(usdt_balance, 1))+'$'  \
                     +'\n[RSI_바이낸스] : ' + str(round(rsi_hour, 2)) + "\n" + '[NOW 가격] : ' + str(round(now_price_binance, 2)) + "$" \
                     + "\n[r0] : " + str(round(RSI_criteria_0, 1)) + "  [g0] : " + str(round(RSI_criteria_0_GetInMoney, 0))+"$" \
                     + "\n[r1] : " + str(round(RSI_criteria_1, 1)) + "  [g1] : " + str(round(RSI_criteria_1_GetInMoney, 0))+"$" \
                     + "\n[r2] : " + str(round(RSI_criteria_2, 1)) + "  [g2] : " + str(round(RSI_criteria_2_GetInMoney, 0))+"$" \
                     + "\n[r3] : " + str(round(RSI_criteria_3, 1)) + "  [g3] : " + str(round(RSI_criteria_3_GetInMoney, 0))+"$"

        # for j, profit_rate_i in enumerate(profit_rate_list):
        #     RSI_string += '[' + str(j + 1) + ". 수익%] : " + str(profit_rate_i) + " 투입 $ : " + str(round(invested_money[j], 1)) + "\n"

        # # 지정가 걸어논 애들이, 매도 되면 알람 오게 함
        # if RSI_info_Binance["Num_input"] > len(invested_money):
        #
        #     profit_messenger = "[RSI_바이낸스_수익화 진행 완료료 알림]"
        #     line_alert.SendMessage_SP(profit_messenger)
        #
        #     # 갯수 새롭게 저장하기 위한 코드
        #     RSI_info_Binance["Num_input"] = len(invested_money)
        #     with open(RSI_info_Binance_path, 'w') as outfile:
        #         json.dump(RSI_info_Binance, outfile)
        #     time.sleep(0.1)
        #
        #
        # elif RSI_info_Binance["Num_input"] == len(invested_money):
        #     pass
        #
        # elif RSI_info_Binance["Num_input"] < len(invested_money):
        #     RSI_info_Binance["Num_input"] = len(invested_money)
        #     with open(RSI_info_Binance_path, 'w') as outfile:
        #         json.dump(RSI_info_Binance, outfile)
        #     time.sleep(0.1)
        if min_flag == 1:
            line_alert.SendMessage_1hourRSI(RSI_string)

        print(1)
        if RSI_on ==1 and rsi_hour <= RSI_criteria_0 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_0"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_0"]) == 0)):
            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_0_GetInMoney / now_price_binance))

            if usdt_balance/now_price_binance < Buy_Amt:
                response = client.transfer_spot_to_margin(asset='BTC', amount=BTCtransferAmt)
                time.sleep(2)
                response = client.create_margin_loan(asset='USDT', amount=GetInMoneyTotal, collateralCoin='BTC')  # 50 USDT as an example
                time.sleep(2)
                result = client.transfer_margin_to_spot(asset='USDT', amount=GetInMoneyTotal)

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            # 비트코인 이제 그냥 모아가기 위해서, 매도 안함
            # print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance*1.05,0)))
            # time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_0"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_0 = "[\U0001F3C2RSI_0_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_0_GetInMoney, 2)) + '$ ' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * 1.05, 0))
            line_alert.SendMessage_SP(rsi_messenger_0)

        elif RSI_on ==1 and rsi_hour <= RSI_criteria_1 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_1"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_1"]) == 0)):
            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_1_GetInMoney / now_price_binance))

            if usdt_balance/now_price_binance < Buy_Amt:
                response = client.transfer_spot_to_margin(asset='BTC', amount=BTCtransferAmt)
                time.sleep(2)
                response = client.create_margin_loan(asset='USDT', amount=GetInMoneyTotal, collateralCoin='BTC')  # 50 USDT as an example
                time.sleep(2)
                result = client.transfer_margin_to_spot(asset='USDT', amount=GetInMoneyTotal)

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            # 비트코인 이제 그냥 모아가기 위해서, 매도 안함
            # print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance*1.05,0)))
            # time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_1"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_1 = "[\U0001F3C2RSI_1_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_1_GetInMoney, 2)) + '$ ' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * 1.05, 0))
            line_alert.SendMessage_SP(rsi_messenger_1)


        elif RSI_on ==1 and rsi_hour <= RSI_criteria_2 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_2"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_2"]) == 0)):

            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_2_GetInMoney / now_price_binance))

            if usdt_balance/now_price_binance < Buy_Amt:
                response = client.transfer_spot_to_margin(asset='BTC', amount=BTCtransferAmt)
                time.sleep(2)
                response = client.create_margin_loan(asset='USDT', amount=GetInMoneyTotal, collateralCoin='BTC')  # 50 USDT as an example
                time.sleep(2)
                result = client.transfer_margin_to_spot(asset='USDT', amount=GetInMoneyTotal)

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            # 비트코인 이제 그냥 모아가기 위해서, 매도 안함
            # print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance * 1.05, 0)))
            # time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_2"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_2 = "[\U0001F3C2RSI_2_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_2_GetInMoney, 2)) + '$' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * 1.05, 0))
            line_alert.SendMessage_SP(rsi_messenger_2)

        elif RSI_on ==1 and rsi_hour <= RSI_criteria_3 and ((timestamp - float(RSI_info_Binance["Pre_RSI_time_3"]) > 86400) or (float(RSI_info_Binance["Pre_RSI_time_3"]) == 0)):

            minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, RSI_criteria_3_GetInMoney / now_price_binance))

            if usdt_balance/now_price_binance < Buy_Amt:
                response = client.transfer_spot_to_margin(asset='BTC', amount=BTCtransferAmt)
                time.sleep(2)
                response = client.create_margin_loan(asset='USDT', amount=GetInMoneyTotal, collateralCoin='BTC')  # 50 USDT as an example
                time.sleep(2)
                result = client.transfer_margin_to_spot(asset='USDT', amount=GetInMoneyTotal)

            print(binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt))
            time.sleep(0.1)
            # 비트코인 이제 그냥 모아가기 위해서, 매도 안함
            # print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, round(now_price_binance * 1.05, 0)))
            # time.sleep(0.1)

            RSI_info_Binance["Pre_RSI_time_3"] = timestamp
            with open(RSI_info_Binance_path, 'w') as outfile:
                json.dump(RSI_info_Binance, outfile)
            time.sleep(0.1)

            rsi_messenger_3 = "[\U0001F3C2RSI_3_바이낸스] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_3_GetInMoney, 2)) + '$' + '\n[현재가 $] : ' + str(round(now_price_binance, 0)) + ' [목표가 $] : ' + str(round(now_price_binance * 1.05, 0))
            line_alert.SendMessage_SP(rsi_messenger_3)

    except Exception as e:
        # 처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
        if RSI_info_Binance['general'][0] == str(e):
            pass
        else:
            #텔레그램 api 오류 5초 이상 쉬어줘야해서 설정
            # time.sleep(5.5)
            print('예외가 발생했습니다.', e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            err = traceback.format_exc()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            line_alert.SendMessage_Trading('[🏂에러 RSI] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))
            if str(e) == "binance Account has insufficient balance for requested action." :
                # Transfer BTC from spot wallet to margin wallet
                try:
                    response = client.transfer_spot_to_margin(asset='BTC', amount=BTCtransferAmt)
                    print("1111")

                    # Get max borrowable amount of USDT against BTC collateral
                    # max_borrowable = client.get_max_margin_loan(asset='USDT', collateralCoin='BTC')
                    # print(max_borrowable)

                    # Borrow USDT against BTC collateral
                    response = client.create_margin_loan(asset='USDT', amount=GetInMoneyTotal, collateralCoin='BTC')  # 50 USDT as an example
                    print("2222")
                    time.sleep(5)
                    result = client.transfer_margin_to_spot(asset='USDT', amount=GetInMoneyTotal)
                    print("3333")
                    # print(response)

                    line_alert.SendMessage_SP("[\U0001F3C2 바이낸스] : RSI 달러 부족")
                except Exception as another_e:
                    print("오류 발생:", another_e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    err = traceback.format_exc()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    line_alert.SendMessage_SP('[🏂에러 RSI loan]')
                    line_alert.SendMessage_Trading('[🏂에러 RSI loan] : \n' + str(err) + '\n[파일] : ' + str(fname) + '\n[라인 넘버] : ' + str(exc_tb.tb_lineno))


        RSI_info_Binance['general'][0] = str(e)
        with open(RSI_info_Binance_path, 'w') as outfile:
            json.dump(RSI_info_Binance, outfile)
        time.sleep(0.1)





