#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert

import json

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)


#내가 매수할 총 코인 개수
MaxCoinCnt = 5.0

#내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()

#TotalMoney = myUpbit.GetTotalMoney(balances) #총 원금

#내 남은 원화(현금))을 구한다.
TotalWon = float(upbit.get_balance("KRW"))


TotalWon = TotalWon * 0.1



#코인당 매수할 매수금액
CoinMoney = TotalWon / MaxCoinCnt

#5천원 이하면 매수가 아예 안되나 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
if CoinMoney < 5000:
    CoinMoney = 5000



print("-----------------------------------------------")
print ("TotalWon:", TotalWon)
print ("CoinMoney:", CoinMoney)



DolPaCoinList = list()

dolpha_type_file_path = "/var/Autobot_seoul/UpbitDolPaCoin.json"
try:
    with open(dolpha_type_file_path, 'r') as json_file:
        DolPaCoinList = json.load(json_file)

except Exception as e:
    print("Exception by First")




DolPaRevenueDict = dict()

revenue_type_file_path = "/var/Autobot_seoul/UpbitDolPaRevenue.json"
try:
    with open(revenue_type_file_path, 'r') as json_file:
        DolPaRevenueDict = json.load(json_file)

except Exception as e:
    print("Exception by First")


stop_revenue = 0.5



time_info = time.gmtime()
hour = time_info.tm_hour
min = time_info.tm_min
print(hour, min)



TopCoinList = myUpbit.GetTopCoinList("day",10)



Tickers = pyupbit.get_tickers("KRW")




for ticker in Tickers:
    try:
        print("Coin Ticker: ",ticker)

        if myUpbit.CheckCoinInList(DolPaCoinList,ticker) == True:


            if hour == 0 and min == 0:

                if myUpbit.IsHasCoin(balances, ticker) == True:
                    revenue_rate = myUpbit.GetRevenueRate(balances, ticker)
                    now_price=pyupbit.get_current_price(ticker)
                    AvgBuyPrice=myUpbit.GetAvgBuyPrice(balances, ticker)
                    NumOfCoin=myUpbit.NumOfTickerCoin(balances, ticker)
                    line_alert.SendMessage("[업빗_돌파_9시매도] : " + ticker + "수익율 : " + str(round(revenue_rate,2))
                                           + " 차익 : "+ str(round((now_price-AvgBuyPrice)*NumOfCoin,2)) + "원" )
                    balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))

                DolPaCoinList.remove(ticker)

                with open(dolpha_type_file_path, 'w') as outfile:
                    json.dump(DolPaCoinList, outfile)



            if myUpbit.IsHasCoin(balances, ticker) == True:

                #수익율을 구한다.
                revenue_rate = myUpbit.GetRevenueRate(balances,ticker)


                if revenue_rate > DolPaRevenueDict[ticker]:

                    DolPaRevenueDict[ticker] = revenue_rate

                    with open(revenue_type_file_path, 'w') as outfile:
                        json.dump(DolPaRevenueDict, outfile)

                else:

                    if revenue_rate > 0.7 and (DolPaRevenueDict[ticker] - stop_revenue) >= revenue_rate:
                        #시장가로 모두 매도!
                        balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))
                        avg_buy_price = myUpbit.GetAvgBuyPrice(balances, ticker)
                        now_price = pyupbit.get_current_price(ticker)
                        AvgBuyPrice = myUpbit.GetAvgBuyPrice(balances, ticker)
                        NumOfCoin = myUpbit.NumOfTickerCoin(balances, ticker)

                        line_alert.SendMessage("[업빗_돌파_TR스탑] : " + ticker + "수익율 : " + str(round(revenue_rate,2))
                                               + " 차익 : "+ str(round((now_price-AvgBuyPrice)*NumOfCoin,2)) + "원" )



        else:
            if myUpbit.CheckCoinInList(TopCoinList,ticker) == False:
                continue

            time.sleep(0.05)
            df = pyupbit.get_ohlcv(ticker,interval="day") #일봉 데이타를 가져온다.


            target_price = float(df['open'][-1]) + (float(df['high'][-2]) - float(df['low'][-2])) * 0.5

            #현재가
            now_price = float(df['close'][-1])

            print(now_price , " > ", target_price)

            if now_price > target_price and len(DolPaCoinList) < MaxCoinCnt: #and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt:



                if myUpbit.IsHasCoin(balances, ticker) == False:



                    print("!!!!!!!!!!!!!!!DolPa GoGoGo!!!!!!!!!!!!!!!!!!!!!!!!")
                    balances = myUpbit.BuyCoinMarket(upbit,ticker,CoinMoney)
                    buy_won = myUpbit.GetCoinNowMoney(balances, ticker)
                    line_alert.SendMessage("[업빗_돌파_시작] : " + ticker + " 총 매수 금액 : " + str(round(buy_won,2)) + "원")


                    DolPaCoinList.append(ticker)

                    with open(dolpha_type_file_path, 'w') as outfile:
                        json.dump(DolPaCoinList, outfile)


                    DolPaRevenueDict[ticker] = 0

                    with open(revenue_type_file_path, 'w') as outfile:
                        json.dump(DolPaRevenueDict, outfile)
                    ##############################################################




    except Exception as e:
        print("---:", e)



