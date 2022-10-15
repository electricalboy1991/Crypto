import pyupbit
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키
import json
import datetime
import time
import line_alert #라인 메세지를 보내기 위함!

RSI_criteria_1 = 30.2
RSI_criteria_2 = 19

RSI_criteria_1_buywon = 150000
RSI_criteria_2_buywon = 400000

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey) #업비트 객체를 만듭니다.


# RSI_info_path = "C:\\Users\world\PycharmProjects\Crypto\RSI_info.json"
RSI_info_path = "/var/Autobot_seoul/RSI_info.json"

RSI_info = dict()

try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(RSI_info_path, 'r', encoding="utf-8") as json_file:
        RSI_info = json.load(json_file)
except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    RSI_info["Pre_RSI_time_1"] = float(0)
    RSI_info["Pre_RSI_time_2"] = float(0)
    print("RSI 파일 없음")

timestamp = datetime.datetime.now().timestamp()
print(timestamp)

#비트코인의 140분봉(캔들) 정보를 가져온다.  
df = pyupbit.get_ohlcv("KRW-BTC",interval="minute60")

#rsi_hour지표를 구합니다.
rsi_hour= float(myUpbit.GetRSI(df,14,-1))

print("BTC_BOT_WORKING")
print("NOW RSI:", rsi_hour)

if rsi_hour <= RSI_criteria_1 and ((float(RSI_info["Pre_RSI_time_1"])-timestamp>86400) or (float(RSI_info["Pre_RSI_time_1"]) ==0)):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!IN")
    print(upbit.buy_market_order("KRW-BTC",RSI_criteria_1_buywon))

    balance_upbit = upbit.get_balances()
    Profit_rate = round(myUpbit.GetRevenueRate(balance_upbit,"KRW-BTC"),1)
    for currency_details in balance_upbit:
        if currency_details['currency'] == 'BTC':
            invested_money=round(float(currency_details['balance'])*float(currency_details['avg_buy_price'])/10000,2)
            break

    rated_money = round((1+Profit_rate/100)*invested_money,2)
    profit_money = round(rated_money-invested_money,2)
    RSI_info["Pre_RSI_time_1"] = timestamp
    with open(RSI_info_path, 'w') as outfile:
        json.dump(RSI_info, outfile)
    time.sleep(0.1)

    rsi_messenger_1="[RSI_1] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_1_buywon / 10000, 2)) + '万'+ ' [투자액] : ' + str(invested_money)+ \
                    ' \n[수익률] : '+ str(Profit_rate)  + ' [평가액] : ' + str(rated_money) +' [차익] : ' + str(profit_money)
    line_alert.SendMessage_SP(rsi_messenger_1)
    
    
elif rsi_hour <= RSI_criteria_2 and ((float(RSI_info["Pre_RSI_time_2"])-timestamp>86400) or (float(RSI_info["Pre_RSI_time_2"]) ==0)):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!IN")
    print(upbit.buy_market_order("KRW-BTC",RSI_criteria_2_buywon))

    balance_upbit = upbit.get_balances()
    Profit_rate = round(myUpbit.GetRevenueRate(balance_upbit,"KRW-BTC"),1)
    for currency_details in balance_upbit:
        if currency_details['currency'] == 'BTC':
            invested_money=round(float(currency_details['balance'])*float(currency_details['avg_buy_price'])/10000,2)
            break

    rated_money = round((1+Profit_rate/100)*invested_money,2)
    profit_money = round(rated_money - invested_money, 2)
    RSI_info["Pre_RSI_time_2"] = timestamp
    with open(RSI_info_path, 'w') as outfile:
        json.dump(RSI_info, outfile)
    time.sleep(0.1)
    rsi_messenger_2="[RSI_2] : " + str(round(rsi_hour, 1)) + ' [금액] : ' + str(round(RSI_criteria_2_buywon / 10000, 2)) + '万'+ ' [투자액] : ' + str(invested_money)+ ' ' \
                    '\n[수익률] : '+ str(Profit_rate) + ' [평가액] : ' + str(rated_money) +' [차익] : ' + str(profit_money)

    line_alert.SendMessage_SP(rsi_messenger_2)




