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

'''
binance_auto_bot.py의 이름을 변경했습니다.

강의를 통해 만든 비트코인을 거래하는 흔들 봇으로 개선된 부분을 아래 코드를 살펴보면서 확인하세요


크론탭에 매 15분마다 실행되게 설정하면 되지만 

*/15 * * * * python3 /var/autobot/binance_auto_BTC.py

30분봉 혹은 5분봉을 볼수도 있는거니 이는 마음 껏 수정하세요!


'''

# 암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

# 암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)

# binance 객체 생성
binance_future = ccxt.binance(config={
    'apiKey': Binance_AccessKey,
    'secret': Binance_ScretKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

binance_spot = ccxt.binance(config={
    'apiKey': Binance_AccessKey,
    'secret': Binance_ScretKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot'
    }
})




# 거래할 코인 티커와 심볼
Target_Coin_Ticker = "BTC/USDT"
Target_Coin_Symbol = "BTCUSDT"

# 이 부분은 소추세는 대추세를 따라간다는 전제하에
# 즉 1시간봉이 상승세라면 15분봉도 상승세고
# 1시간봉이 하락세면 15분봉도 하락일 확율이 높다는 가정입니다.

# 아래 처럼 1시간봉 캔들 정보 가져와 5일 이동평균선 구한뒤에

time.sleep(0.1)
df_up_future = myBinance.GetOhlcv(binance_future, Target_Coin_Ticker, '1h')
df_up_spot = myBinance.GetOhlcv(binance_spot, Target_Coin_Ticker, '1h')


time.sleep(0.1)

# 캔들 정보 가져온다 여기서는 15분봉을 보지만 자유롭게 조절 하세요!!!
df_future = myBinance.GetOhlcv(binance_future, Target_Coin_Ticker, '15m')
df_spot= myBinance.GetOhlcv(binance_spot, Target_Coin_Ticker, '15m')


# 영상엔 없지만 레버리지를 3으로 셋팅합니다!
try:
    print(binance_future.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': 3}))
except Exception as e:
    print("----:", e)
# 앱이나 웹에서 레버리지를 바뀌면 바뀌니깐 주의하세요!!
#################################################################################################################


# 잔고 데이타 가져오기
balance_future = binance_future.fetch_balance(params={"type": "future"})
time.sleep(0.1)
balance_spot = binance_spot.fetch_balance(params={"type": "spot"})
time.sleep(0.1)


amt = 0  # 수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
entryPrice = 0  # 평균 매입 단가. 따라서 물을 타면 변경 된다.
leverage = 1  # 레버리지, 앱이나 웹에서 설정된 값을 가져온다.
unrealizedProfit = 0  # 미 실현 손익..그냥 참고용

isolated = True  # 격리모드인지

# 실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
for posi in balance_future['info']['positions']:
    if posi['symbol'] == Target_Coin_Symbol:
        amt = float(posi['positionAmt'])
        entryPrice = float(posi['entryPrice'])
        leverage = float(posi['leverage'])
        unrealizedProfit = float(posi['unrealizedProfit'])
        isolated = posi['isolated']
        break


#################################################################################################################
# 영상엔 없지만 격리모드가 아니라면 격리모드로 처음 포지션 잡기 전에 셋팅해 줍니다,.
if isolated == False:
    try:
        print(binance_future.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
    except Exception as e:
        print("----:", e)

# 해당 코인 가격을 가져온다.
coin_price_future = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)
coin_price_spot = myBinance.GetCoinNowPrice(binance_spot, Target_Coin_Ticker)

# 레버리지에 따른 최대 매수 가능 수량
# 만약에 내가 2000원이 있어, 전재산의 0.5를 쓸거야, 레버리지는 3배, 코인 가격은 1000원, 이때 Max_Amount는 3이 되는거지
Max_Amount = round(myBinance.GetAmount(float(balance['USDT']['total']), coin_price, 0.5), 3) * leverage

# 최대 매수수량의 1%에 해당하는 수량을 구한다.
one_percent_amount = Max_Amount / 100.0

print("one_percent_amount : ", one_percent_amount)

# 첫 매수 비중을 구한다.. 여기서는 5%!
# * 20.0 을 하면 20%가 되겠죠? 마음껏 조절하세요!
first_amount = one_percent_amount * 5.0

# 영상엔 없지만 이렇게 코인의 최소주문 수량을 받아올 수 있습니다!
# 즉 비트코인의 경우 0.001로 그보다 작은 수량으로 주문을 넣으면 오류가 납니다.!
# 최소 주문 수량을 가져온다
# 해당 함수는 수강생 분이 만드신 걸로 아래 링크를 참고하세요!
# https://blog.naver.com/zhanggo2/222722244744
minimun_amount = myBinance.GetMinimumAmount(binance_future, Target_Coin_Ticker)

# minimun_amount 안에는 최소 주문수량이 들어가 있습니다. 비트코인이니깐 0.001보다 작다면 0.001개로 셋팅해줍니다.
if first_amount < minimun_amount:
    first_amount = minimun_amount

print("first_amount : ", first_amount)

# 음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다.
abs_amt = abs(amt)

# 아래는 타겟 수익율로 마음껏 조절하세요
# 타겟 레이트 0.001
target_rate = 0.001
# 타겟 수익율 0.1%
target_revenue_rate = target_rate * 100.0

# 스탑로스 비율설정 0.5는 원금의 마이너스 50%를 의미한다. 0.1은 마이너스 10%
stop_loass_rate = 0.5

# 0이면 포지션 잡기전
if amt == 0:
    print("-----------------------------No Position---------------------------------")

    # 5일선이 20일선 위에 있는데 5일선이 하락추세로 꺾였을때 and RSI지표가 35 이상일때 숏 떨어질거야 를 잡는다.
    if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5 and rsi14 >= 35.0:
        print("sell/short")
        # 주문 취소후
        binance_future.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)

        '''
        #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 잡힌다는 보장이 없다는 점입니다.


        #해당 코인 가격을 가져온다.
        coin_price = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)

        #숏 포지션을 잡는다
        print(binance_future.create_limit_sell_order(Target_Coin_Ticker, first_amount, coin_price))

        '''
        # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요!
        # 숏 포지션을 잡는다
        line_alert.SendMessage("[바이_흔들봇]숏 포지션 잡기로 시작 : " + str(round(coin_price * first_amount, 2)) + "$")
        print(binance_future.create_market_sell_order(Target_Coin_Ticker, first_amount))

        # 스탑 로스 설정을 건다.
        myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)

    # 5일선이 20일선 아래에 있는데 5일선이 상승추세로 꺾였을때 and RSI지표가 65 이하일때  롱 오를거야 를 잡는다.
    if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5 and rsi14 <= 40.0:
        print("buy/long")
        # 주문 취소후
        binance_future.cancel_all_orders(Target_Coin_Ticker)
        time.sleep(0.1)

        '''
        #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 잡힌다는 보장이 없다는 점입니다.



        #해당 코인 가격을 가져온다.
        coin_price = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)

        #롱 포지션을 잡는다
        print(binance_future.create_limit_buy_order(Target_Coin_Ticker, first_amount, coin_price))

        '''
        # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요!
        # 롱 포지션을 잡는다
        line_alert.SendMessage("[바이_흔들봇]롱 포지션 잡기로 시작 : " + str(round(coin_price * first_amount, 2)) + "$")
        print(binance_future.create_market_buy_order(Target_Coin_Ticker, first_amount))

        # 스탑 로스 설정을 건다.
        myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)



# 0이 아니라면 포지션 잡은 상태
else:
    print("------------------------------------------------------")

    # 현재까지 구매한 퍼센트! 즉 비중!! 현재 보유 수량을 1%의 수량으로 나누면 된다.
    buy_percent = abs_amt / one_percent_amount
    print("Buy Percent : ", buy_percent)

    # 수익율을 구한다!
    revenue_rate = (coin_price - entryPrice) / entryPrice * 100.0
    # 단 숏 포지션일 경우 수익이 나면 마이너스로 표시 되고 손실이 나면 플러스가 표시 되므로 -1을 곱하여 바꿔준다.
    if amt < 0:
        revenue_rate = revenue_rate * -1.0

    # 레버리지를 곱한 실제 수익율
    leverage_revenu_rate = revenue_rate * leverage

    print("Revenue Rate : ", revenue_rate, ", Real Revenue Rate : ", leverage_revenu_rate)

    # 손절 마이너스 수익율을 셋팅한다.
    danger_rate = -5.0
    # 레버리지를 곱한 실제 손절 할 마이너스 수익율
    # 레버리지를 곱하고 난 여기가 실제 내 원금 대비 실제 손실율입니다!
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

    # 물탈 기준 마이너스 수익율과 스탑로스 비율도 보유 비중에 따라 조절할 수 있습니다.
    # 어디까지나 예시이며 제가 설정한 이 부분은 언제든 변경될 수 있습니다.
    # 여러분도 여러분만의 비중 조절로 바꿔서 코딩하세요!

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

        # 5일선이 20일선 밑에 있고 상승추세로 전환된 듯 보이는 롱 포지션을 잡을만한 상황!!!!
        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5:
            # 수익이 났다!!! 숏 포지션 종료하고 롱 포지션도 잡아주자!
            if revenue_rate >= target_revenue_rate:
                if rsi14 <= 35:
                    # 알림 기능 테스트! 자유롭게 원하는 부분에 내게 메세지를 보내보세요! 단 숫자형(실수,정수)는 저렇게 str함수로 스트링으로 변환이 필요하다는 점 기억하세요!
                    line_alert.SendMessage("[바이_흔들봇]수익 실현 : " + str(
                        round(unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100), 2)) + "$")
                    line_alert.SendMessage("[바이_흔들봇]수익% :(lev " + str(leverage) + ")"
                                           + str(round(
                        leverage * (unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100)) * 100 / (
                                    abs_amt * coin_price), 2)) + "%")
                    # 주문 취소후
                    binance_future.cancel_all_orders(Target_Coin_Ticker)
                    time.sleep(0.1)

                    # 롱 포지션을 잡는다
                    print(binance_future.create_market_buy_order(Target_Coin_Ticker, abs_amt + first_amount))
                else:
                    # 알림 기능 테스트! 자유롭게 원하는 부분에 내게 메세지를 보내보세요! 단 숫자형(실수,정수)는 저렇게 str함수로 스트링으로 변환이 필요하다는 점 기억하세요!
                    line_alert.SendMessage("[바이_흔들봇]수익 실현 : " + str(
                        round(unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100), 2)) + "$")
                    line_alert.SendMessage("[바이_흔들봇]수익% :(lev " + str(leverage) + ")"
                                           + str(round(
                        leverage * (unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100)) * 100 / (
                                    abs_amt * coin_price), 2)) + "%")
                    # 주문 취소후
                    binance_future.cancel_all_orders(Target_Coin_Ticker)
                    time.sleep(0.1)

                    # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요!
                    # 롱 포지션을 잡는다
                    print(binance_future.create_market_buy_order(Target_Coin_Ticker, abs_amt))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)

        # 즉 5일 선이 20일 선 위에 있고 하락추세로 꺾였을 때 물을 탑니다.
        # 즉 숏 포지션을 잡을만한 상황!!!!
        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:

            # 물탈 수량 여기서는 현재 수량(abs_amt)만큼 물을 타지만
            # water_amount = one_percent_amount * 5.0 이렇게 5%씩 탄다는 식으로 변형할 수 있습니다!!
            # 아래 수식의 의미는 지금 가지고 있는 만큼 물탄다
            water_amount = abs_amt

            # 5 - 10 - 20 - 40 - 80 이렇게 가다가, 마지막 20이 남은 상태를 걸러내기 위한 if문
            if Max_Amount < abs_amt + water_amount:
                water_amount = Max_Amount - abs_amt

            # 물탈 마이너스 수익율 보다 내 수익율이 작다면 물을 타자!!
            if revenue_rate <= water_rate and Max_Amount >= abs_amt + water_amount:
                # 주문 취소후
                binance_future.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)

                '''
                #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 잡힌다는 보장이 없다는 점입니다.

                #해당 코인 가격을 가져온다.
                coin_price = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)

                #숏 포지션을 잡는다
                print(binance_future.create_limit_sell_order(Target_Coin_Ticker, water_amount, coin_price))

                '''
                # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요!
                # 숏 포지션을 잡는다
                line_alert.SendMessage("[바이_흔들봇]물타기 : " + str(round(water_amount * coin_price, 2)) + "$")
                print(binance_future.create_market_sell_order(Target_Coin_Ticker, water_amount))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)

        # 내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:
            # 주문 취소후
            binance_future.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)
            '''
            #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 종료되거나 잡힌다는 보장이 없다는 점입니다.

            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)

            #롱 포지션을 잡는다
            print(binance_future.create_limit_buy_order(Target_Coin_Ticker, abs_amt / 2.0, coin_price))
            '''
            # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요
            # 롱 포지션을 잡는다
            line_alert.SendMessage("[바이_흔들봇] 추가 물타기 위해 절반 손절 : " + str(round(abs_amt / 2.0 * coin_price, 2)) + "$")
            print(binance_future.create_market_buy_order(Target_Coin_Ticker, abs_amt / 2.0))

            # 스탑 로스 설정을 건다.
            myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)





    # 양수면 롱 포지션 상태
    else:
        print("-----Long Position")

        # 5일선이 20일선 위에 있고 하락 추세로 보일때! 숏 포지션을 잡을만한 상황!!!!
        if ma5 > ma20 and ma5_before3 < ma5_before2 and ma5_before2 > ma5:
            # 수익이 났다!!! 롱 포지션 종료하고 숏 포지션도 잡아주자!
            if revenue_rate >= target_revenue_rate:
                # 알림 기능 테스트! 자유롭게 원하는 부분에 내게 메세지를 보내보세요! 단 숫자형(실수,정수)는 저렇게 str함수로 스트링으로 변환이 필요하다는 점 기억하세요!
                line_alert.SendMessage("[바이_흔들봇]수익 실현 : " + str(
                    round(unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100), 2)) + "$")
                line_alert.SendMessage("[바이_흔들봇]수익% :(lev " + str(leverage) + ")"
                                       + str(round(
                    leverage * (unrealizedProfit - (abs_amt + first_amount) * coin_price * (0.04 / 100)) * 100 / (
                                abs_amt * coin_price), 2)) + "%")
                # 주문 취소후
                binance_future.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                '''
                #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 종료되거나 잡힌다는 보장이 없다는 점입니다.


                #해당 코인 가격을 가져온다.
                coin_price = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)

                #숏 포지션을 잡는다
                print(binance_future.create_limit_sell_order(Target_Coin_Ticker, abs_amt + first_amount, coin_price))
                '''
                # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요!
                # 숏 포지션을 잡는다
                print(binance_future.create_market_sell_order(Target_Coin_Ticker, abs_amt + first_amount))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)

        # 즉 5일 선이 20일 선 아래에 있고 상승추세로 꺾였을 때 물을 탑니다.
        # 롱 포지션을 잡을만한 상황!!!!
        if ma5 < ma20 and ma5_before3 > ma5_before2 and ma5_before2 < ma5:

            # 물탈 수량 여기서는 현재 수량(abs_amt)만큼 물을 타지만
            # water_amount = one_percent_amount * 5.0 이렇게 5%씩 탄다는 식으로 변형할 수 있습니다!!
            water_amount = abs_amt

            if Max_Amount < abs_amt + water_amount:
                water_amount = Max_Amount - abs_amt

            # 물탈 마이너스 수익율 보다 내 수익율이 작다면 물을 타자!!
            if revenue_rate <= water_rate and Max_Amount >= abs_amt + water_amount:
                # 주문 취소후
                binance_future.cancel_all_orders(Target_Coin_Ticker)
                time.sleep(0.1)
                '''
                #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 잡힌다는 보장이 없다는 점입니다.

                #해당 코인 가격을 가져온다.
                coin_price = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)

                #롱 포지션을 잡는다
                print(binance_future.create_limit_buy_order(Target_Coin_Ticker, water_amount, coin_price))

                '''
                # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요!

                # 롱 포지션을 잡는다
                line_alert.SendMessage("[바이_흔들봇]물타기 : " + str(round(water_amount * coin_price, 2)) + "$")
                print(binance_future.create_market_buy_order(Target_Coin_Ticker, water_amount))

                # 스탑 로스 설정을 건다.
                myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)

        # 내 보유 수량의 절반을 손절한다 단!! 매수 비중이 90% 이상이면서 내 수익율이 손절 마이너스 수익율보다 작을 때
        if revenue_rate <= danger_rate and buy_percent >= 90.0:
            # 주문 취소후
            binance_future.cancel_all_orders(Target_Coin_Ticker)
            time.sleep(0.1)
            '''
            #클래스에선 수수료 절감 차원에서 지정가로 잡았지만 단점은 100% 포지션이 종료되거나 잡힌다는 보장이 없다는 점입니다.

            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binance_future, Target_Coin_Ticker)

            #숏 포지션을 잡는다
            print(binance_future.create_limit_sell_order(Target_Coin_Ticker, abs_amt / 2.0, coin_price))
            '''
            # 따라서 여기서는 시장가로 잡습니다 <- 이렇게 하는걸 권장드려요!
            # 숏 포지션을 잡는다
            line_alert.SendMessage("[바이_흔들봇]물타기 위해 절반 손절 : " + str(round(abs_amt / 2.0 * coin_price, 2)) + "$")
            print(binance_future.create_market_sell_order(Target_Coin_Ticker, abs_amt / 2.0))

            # 스탑 로스 설정을 건다.
            myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)

# 지정가 주문만 있기 때문에 혹시나 스탑로스가 안걸릴 수 있어서 마지막에 한번 더 건다
# 해당 봇이 서버에서 주기적으로 실행되기 때문에 실행 될때마다 체크해서 걸어 줄 수 있다.
# 스탑 로스 설정을 건다. 포지션 잡은 수량이 있을때만 실행 되게 조건을 추가했다.
if amt != 0:
    myBinance.SetStopLoss(binance_future, Target_Coin_Ticker, stop_loass_rate)







