import ccxt
import time
import pandas as pd
import pprint
# pprint로하면, 정렬되어서 나옴


#챕터7까지 진행하시면서 봇은 점차 완성이 되어 갑니다!!!
#챕터6까지 완강 후 봇을 돌리셔도 되지만 이왕이면 7까지 완강하신 후 돌리시는 걸 추천드려요!


access = "15XXj7UPGD5dkBQK4zeFJMuqjQeEce9P6MuPIRdIhhzKUDCFuZoQsvjfKiP2sRaY"          # 본인 값으로 변경
secret = "tjJlMeq25x4aOdThgq3DHr5bHhtkmZIOBLTMiulht2NBlTQbH0H0EA4FaznwNYtK"          # 본인 값으로 변경

# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': access, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

#포지션 잡을 코인을 설정합니다.
Target_Coin_Ticker = "BTC/USDT"
Target_Coin_Symbol = "BTCUSDT"

#해당 코인의 정보를 가져옵니다
btc = binance.fetch_ticker(Target_Coin_Ticker)
#현재 종가 즉 현재가를 읽어옵니다.
btc_price = btc['close']

print(btc['close'])


#시장가 taker 0.04, 지정가 maker 0.02

#시장가 숏 포지션 잡기 
#print(binance.create_market_sell_order(Target_Coin_Ticker, 0.002))

#시장가 롱 포지션 잡기 
#print(binance.create_market_buy_order(Target_Coin_Ticker, 0.001))

time.sleep(0.1)

#잔고 데이타 가져오기 
balance = binance.fetch_balance(params={"type": "future"})
#pprint.pprint(balance)

print(balance['USDT'])
#밸런스 그냥 출력하면, 너무 많은 정보가 나옴. 그래서 수정해줘야함.

amt = 0 #수량 정보 0이면 매수전(포지션 잡기 전), 양수면 롱 포지션 상태, 음수면 숏 포지션 상태
entryPrice = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
leverage = 1   #레버리지, 앱이나 웹에서 설정된 값을 가져온다.
unrealizedProfit = 0 #미 실현 손익..그냥 참고용 

#실제로 잔고 데이타의 포지션 정보 부분에서 해당 코인에 해당되는 정보를 넣어준다.
for posi in balance['info']['positions']:
    if posi['symbol'] == Target_Coin_Symbol:
        leverage = float(posi['leverage'])
        entryPrice = float(posi['entryPrice'])#평균 매입 단가
        unrealizedProfit = float(posi['unrealizedProfit'])# 미실현 수익 금액
        amt = float(posi['positionAmt'])#amt = amount 포지션 수량

print("amt:",amt)
print("entryPrice:",entryPrice)
print("leverage:",leverage)
print("unrealizedProfit:",unrealizedProfit)

#음수를 제거한 절대값 수량 ex -0.1 -> 0.1 로 바꿔준다.
abs_amt = abs(amt)

#0.1%증가한 금액을 의미합니다. 이건 롱포지션 종료할 때 수익
entryPrice = entryPrice * 1.001


#0.1%감소 금액을 의미합니다. 이건 숏포지션 종료할 때 수익, 숏은 가격이 떨어져야 수익이니까
# entryPrice = entryPrice * 0.999

#지정가 숏 포지션 잡기 
#print(binance.create_limit_sell_order(Target_Coin_Ticker, abs_amt, entryPrice))

#지정가 롱 포지션 잡기 
#print(binance.create_limit_buy_order(Target_Coin_Ticker, abs_amt, entryPriceㄴ))








