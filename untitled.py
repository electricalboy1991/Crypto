"""
RSI랑 추세선 이용해서 바닥예상지정 오르는 추세에 사고, 꼭지예상지점에서 떨어지는 추세에 파는 흔들 봇
"""

import ccxt
import time
import pandas as pd
import pprint

import myBinance
import ende_key  # 암복호화키
import my_key  # 업비트 시크릿 액세스키

import line_alert  # 라인 메세지를 보내기 위함!



# 암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

# 암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)

# binance 객체 생성
binanceX = ccxt.binance(config={
    'apiKey': Binance_AccessKey,
    'secret': Binance_ScretKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# 거래할 코인 티커와 심볼
Target_Coin_Ticker = "BTC/USDT"
Target_Coin_Symbol = "BTCUSDT"


time.sleep(0.1)
df_up = myBinance.GetOhlcv(binanceX, Target_Coin_Ticker, '1h')

ma5_up_before2 = myBinance.GetMA(df_up, 5, -3)
ma5_up = myBinance.GetMA(df_up, 5, -2)



time.sleep(0.1)

df = myBinance.GetOhlcv(binanceX, Target_Coin_Ticker, '15m')

# 최근 3개의 종가 데이터
print("Price: ", df['close'][-3], "->", df['close'][-2], "->", df['close'][-1])
# 최근 3개의 5일선 데이터
print("5ma: ", myBinance.GetMA(df, 5, -3), "->", myBinance.GetMA(df, 5, -2), "->", myBinance.GetMA(df, 5, -1))
# 최근 3개의 RSI14 데이터
print("RSI14: ", myBinance.GetRSI(df, 14, -3), "->", myBinance.GetRSI(df, 14, -2), "->", myBinance.GetRSI(df, 14, -1))

# 최근 5일선 3개를 가지고 와서 변수에 넣어준다.
ma5_before3 = myBinance.GetMA(df, 5, -4)
ma5_before2 = myBinance.GetMA(df, 5, -3)
ma5 = myBinance.GetMA(df, 5, -2)

# 20일선을 가지고 와서 변수에 넣어준다.
ma20 = myBinance.GetMA(df, 20, -2)

# RSI14 정보를 가지고 온다.
rsi14 = myBinance.GetRSI(df, 14, -1)


try:
    print(binanceX.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': 3}))
except Exception as e:
    print("----:", e)
# 앱이나 웹에서 레버리지를 바뀌면 바뀌니깐 주의하세요!!
#################################################################################################################


# 잔고 데이타 가져오기
balance = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)
# pprint.pprint(balance)


print(balance['USDT'])
print("Total Money:", float(balance['USDT']['total']))
print("Remain Money:", float(balance['USDT']['free']))

amt = 0  # 수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
entryPrice = 0  # 평균 매입 단가. 따라서 물을 타면 변경 된다.
leverage = 1  # 레버리지, 앱이나 웹에서 설정된 값을 가져온다.
unrealizedProfit = 0  # 미 실현 손익..그냥 참고용

isolated = True  # 격리모드인지

# 실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
for posi in balance['info']['positions']:
    if posi['symbol'] == Target_Coin_Symbol:
        amt = float(posi['positionAmt'])
        entryPrice = float(posi['entryPrice'])
        leverage = float(posi['leverage'])
        unrealizedProfit = float(posi['unrealizedProfit'])
        isolated = posi['isolated']
        break

if isolated == False:
    try:
        print(binanceX.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
    except Exception as e:
        print("----:", e)

print("amt:", amt)
print("entryPrice:", entryPrice)
print("leverage:", leverage)
print("unrealizedProfit:", unrealizedProfit)

# 해당 코인 가격을 가져온다.
coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)


Max_Amount = round(myBinance.GetAmount(float(balance['USDT']['total']), coin_price, 0.5), 3) * leverage

one_percent_amount = Max_Amount / 100.0

print("one_percent_amount : ", one_percent_amount)


first_amount = one_percent_amount * 5.0


minimun_amount = myBinance.GetMinimumAmount(binanceX, Target_Coin_Ticker)

if first_amount < minimun_amount:
    first_amount = minimun_amount

print("first_amount : ", first_amount)


abs_amt = abs(amt)

target_rate = 0.001
# 타겟 수익율 0.1%
target_revenue_rate = target_rate * 100.0

stop_loass_rate = 0.5

# 0이면 포지션 잡기전
if amt == 0:
    print("-----------------------------No Position---------------------------------")

    # 5일선이 20일선 위에 있는데 5일선이 하락추세로 꺾였을때 and RSI지표가 35 이상일때 숏 떨어질거야 를 잡는다.
    if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5 and rsi14 >= 35.0:
        print("sell/short")
        # 주문 취소후
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)

        print(binanceX.create_market_sell_order(Target_Coin_Ticker, first_amount))

        # 스탑 로스 설정을 건다.
        myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)

    # 5일선이 20일선 아래에 있는데 5일선이 상승추세로 꺾였을때 and RSI지표가 65 이하일때  롱 오를거야 를 잡는다.
    if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and rsi14 <= 65.0:
        print("buy/long")
        # 주문 취소후
        binanceX.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)


        print(binanceX.create_market_buy_order(Target_Coin_Ticker, first_amount))

        # 스탑 로스 설정을 건다.
        myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)



# 0이 아니라면 포지션 잡은 상태
else:
    print("------------------------------------------------------")

    # 현재까지 구매한 퍼센트! 즉 비중!! 현재 보유 수량을 1%의 수량으로 나누면 된다.
    buy_percent = abs_amt / one_percent_amount
    print("Buy Percent : ", buy_percent)

    # 수익율을 구한다!
    revenue_rate = (coin_price - entryPrice) / entryPrice * 100.0
    if amt < 0:
        revenue_rate = revenue_rate * -1.0

    # 레버리지를 곱한 실제 수익율
    leverage_revenu_rate = revenue_rate * leverage

    print("Revenue Rate : ", revenue_rate, ", Real Revenue Rate : ", leverage_revenu_rate)

    # 손절 마이너스 수익율을 셋팅한다.
    danger_rate = -5.0

    leverage_danger_rate = danger_rate * leverage

    print("Danger Rate : ", danger_rate, ", Real Danger Rate : ", leverage_danger_rate)

    '''
    5  + 5
    10  + 10
    20   + 20
    40   + 40
    80  + 20

    '''

    # 추격 매수 즉 물 탈 마이너스 수익율을 셋팅한다.
    water_rate = -1.0


    if buy_percent <= 5.0:
        water_rate = -0.5  # 실제 코인 시세가 -0.5%
        stop_loass_rate = 0.9  # 스탑 로스 -90%
    elif buy_percent <= 10.0:
        water_rate = -1.0  # 실제 코인 시세가 -1.0%
        stop_loass_rate = 0.7  # 스탑 로스 -70%
    elif buy_percent <= 20.0:
        water_rate = -2.0  # 실제 코인 시세가 -2.0%
        stop_loass_rate = 0.5  # 스탑 로스 -50%
    elif buy_percent <= 40.0:
        water_rate = -3.0  # 실제 코인 시세가 -3.0%
        stop_loass_rate = 0.4  # 스탑 로스 -40%
    elif buy_percent <= 80.0:
        water_rate = -5.0  # 실제 코인 시세가 -5.0%
        stop_loass_rate = 0.3  # 스탑 로스 -30%

    # 레버리지를 곱한 실제 물 탈 마이너스 수익율
    leverage_danger_rate = water_rate * leverage

    print("Water Rate : ", water_rate, ", Real Water Rate : ", leverage_danger_rate)

    # 음수면 숏 포지션 상태
    if amt < 0:
        print("-----Short Position")

        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5:
            if revenue_rate >= target_revenue_rate:
                if rsi14 <= 35:
                    line_alert.SendMessage("[바이_흔들봇]수익 실현 : " + str(
                        round(unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100), 2)) + "$")
                    line_alert.SendMessage("[바이_흔들봇]수익% :(lev " + str(leverage) + ")"
                                           + str(round(
                        leverage * (unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100)) * 100 / (
                                    abs_amt * coin_price), 2)) + "%")
                    # 주문 취소후
                    binanceX.cancel_all_orders(Target_Coin_Ticker)
                    time.sleep(0.1)

                    # 롱 포지션을 잡는다
                    print(binanceX.create_market_buy_order(Target_Coin_Ticker, abs_amt + first_amount))
                else:
                    line_alert.SendMessage("[바이_흔들봇]수익 실현 : " + str(
                        round(unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100), 2)) + "$")
                    line_alert.SendMessage("[바이_흔들봇]수익% :(lev " + str(leverage) + ")"
                                           + str(round(
                        leverage * (unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100)) * 100 / (
                                    abs_amt * coin_price), 2)) + "%")
                    # 주문 취소후
                    binanceX.cancel_all_orders(Target_Coin_Ticker)
                    time.sleep(0.1)

                    print(binanceX.create_market_buy_order(Target_Coin_Ticker, abs_amt))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)

        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:

            water_amount = abs_amt

            # 5 - 10 - 20 - 40 - 80 이렇게 가다가, 마지막 20이 남은 상태를 걸러내기 위한 if문
            if Max_Amount < abs_amt + water_amount:
                water_amount = Max_Amount - abs_amt

            # 물탈 마이너스 수익율 보다 내 수익율이 작다면 물을 타자!!
            if revenue_rate <= water_rate and Max_Amount >= abs_amt + water_amount:
                # 주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)


                line_alert.SendMessage("[바이_흔들봇]물타기 : " + str(round(water_amount * coin_price, 2)) + "$")
                print(binanceX.create_market_sell_order(Target_Coin_Ticker, water_amount))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)

        # 내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:
            # 주문 취소후
            binanceX.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)
            '''
            #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 종료되거나 잡힌다는 보장이 없다는 점입니다.

            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)

            #롱 포지션을 잡는다
            print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs_amt / 2.0, coin_price))
            '''

            line_alert.SendMessage("[바이_흔들봇]물타기 위해 절반 손절 : " + str(round(abs_amt / 2.0 * coin_price, 2)) + "$")
            print(binanceX.create_market_buy_order(Target_Coin_Ticker, abs_amt / 2.0))

            # 스탑 로스 설정을 건다.
            myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)





    # 양수면 롱 포지션 상태
    else:
        print("-----Long Position")

        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:
            if revenue_rate >= target_revenue_rate:
                line_alert.SendMessage("[바이_흔들봇]수익 실현 : " + str(
                    round(unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100), 2)) + "$")
                line_alert.SendMessage("[바이_흔들봇]수익% :(lev " + str(leverage) + ")"
                                       + str(round(
                    leverage * (unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100)) * 100 / (
                                abs_amt * coin_price), 2)) + "%")
                # 주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)


                print(binanceX.create_market_sell_order(Target_Coin_Ticker, abs_amt + first_amount))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)


        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5:


            water_amount = abs_amt

            if Max_Amount < abs_amt + water_amount:
                water_amount = Max_Amount - abs_amt

            if revenue_rate <= water_rate and Max_Amount >= abs_amt + water_amount:
                # 주문 취소후
                binanceX.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)


                # 롱 포지션을 잡는다
                line_alert.SendMessage("[바이_흔들봇]물타기 : " + str(round(water_amount * coin_price, 2)) + "$")
                print(binanceX.create_market_buy_order(Target_Coin_Ticker, water_amount))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)

        # 내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:
            binanceX.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)

            line_alert.SendMessage("[바이_흔들봇]물타기 위해 절반 손절 : " + str(round(abs_amt / 2.0 * coin_price, 2)) + "$")
            print(binanceX.create_market_sell_order(Target_Coin_Ticker, abs_amt / 2.0))

            # 스탑 로스 설정을 건다.
            myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)


if amt != 0:
    myBinance.SetStopLoss(binanceX, Target_Coin_Ticker, stop_loass_rate)







