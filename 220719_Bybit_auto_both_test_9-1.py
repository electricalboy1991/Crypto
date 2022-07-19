import ccxt
import time
import pandas as pd
import pprint

import myBybit
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBybit.SimpleEnDecrypt(ende_key.ende_key)


#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Bybit_AccessKey = simpleEnDecrypt.decrypt(my_key.bybit_access)
Bybit_ScretKey = simpleEnDecrypt.decrypt(my_key.bybit_secret)

# bybit 객체 생성
bybitX = ccxt.bybit(config={
    'apiKey': Bybit_AccessKey, 
    'secret': Bybit_ScretKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})



#선물 마켓에서 거래중인 모든 코인을 가져옵니다.
Tickers = bybitX.fetch_tickers()



#나의 코인
LovelyCoinList = ['BTC/USDT:USDT']





#모든 선물 거래가능한 코인을 가져온다.
for ticker in Tickers:

    try: 

   
        #하지만 여기서는 USDT 테더로 살수 있는 모든 선물 거래 코인들을 대상으로 돌려봅니다.
        if "/USDT" in ticker:
            Target_Coin_Ticker = ticker

            #러블리 코인이 아니라면 스킵! 러블리 코인만 대상으로 한다!!
            if myBybit.CheckCoinInList(LovelyCoinList,ticker) == False:
                continue

            
            time.sleep(0.5)
            
            Target_Coin_Symbol = ticker.replace("/", "").replace(":USDT","")


            print("--------0--------", ticker)


            time.sleep(0.05)
            #최소 주문 수량을 가져온다 
            minimun_amount = myBybit.GetMinimumAmount(bybitX,Target_Coin_Symbol)

            print("minimun_amount : ", minimun_amount)



            leverage = 10 #레버리지 10
            test_amt = 0.001 #테스트할 수량!




            #################################################################################################################
            #레버리지를 3으로 그리고 격리모드 셋팅합니다! 필요없다면 주석처리 하세요!
            print("###############")
            #교차 모드로 했다가 다시 격리모드로 설정하는 이유는 이미 교차모드일 경우 레버리지만 변경할려는 경우 이미 교차여서 레버리지 수정이 안되는 현상이 발견되어
            #이렇게 교차모드와 레버리지 설정했다가 다시 격리모드로 설정하는 식으로 보완을 했습니다!
            try:
                print(bybitX.set_margin_mode("CROSS",Target_Coin_Symbol, {'leverage':leverage}))
            except Exception as e:
                print("---:", e)

            try:
                print(bybitX.set_margin_mode("ISOLATED",Target_Coin_Symbol, {'leverage':leverage}))
            except Exception as e:
                print("---:", e)


            time.sleep(0.2)

            #################################################################################################################



            #잔고 데이타 가져오기 
            balances2 = bybitX.fetch_positions(None, {'type':'Future'})
            time.sleep(0.1)



            amt_s = 0 
            amt_b = 0
            entryPrice_s = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
            entryPrice_b = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.



            target_rate = 0.01 #목표 수익율



            #숏 잔고
            for posi in balances2:
                if posi['info']['symbol'] == Target_Coin_Symbol and posi['info']['side'] == "Sell":
                    amt_s = float(posi['info']['size'])
                    entryPrice_s = float(posi['info']['entry_price'])
                    leverage = float(posi['info']['leverage'])
                    break

            #롱 잔고
            for posi in balances2:
                if posi['info']['symbol'] == Target_Coin_Symbol and posi['info']['side'] == "Buy":
                    amt_b = float(posi['info']['size'])
                    entryPrice_b = float(posi['info']['entry_price'])
                    leverage = float(posi['info']['leverage'])
                    break
                    
            
                    

            #해당 코인 가격을 가져온다.
            coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)



            
            #롱 포지션이 없을 경우
            if abs(amt_b) == 0:

            
                #롱 시장가 주문!
                data = bybitX.create_market_buy_order(Target_Coin_Ticker, test_amt)


                #해당 코인 가격을 가져온다.
                coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)

                
                #예로 1% 상승한 가격에 지정가 주문으로 롱 포지션 종료하려면..
                target_price = coin_price * (1.0 + target_rate)
                            

                #롱 포지션 지정가 종료 주문!!     
                print(bybitX.create_limit_sell_order(Target_Coin_Ticker, test_amt, target_price, {'reduce_only': True,'close_on_trigger':True}))

                stop_price = coin_price * (1.0 - target_rate)


                #스탑로스!
                myBybit.SetStopLossLongPrice(bybitX,Target_Coin_Ticker,stop_price)
                

            else:
                #롱 포지션이 있는 경우
                if abs(amt_b) > 0:
                    #롱 수익율을 구한다!
                    revenue_rate_b = (coin_price - entryPrice_b) / entryPrice_b * 100.0

                    print("revenue_rate_b : ", revenue_rate_b)

            


            #숏 포지션이 없을 경우
            if abs(amt_s) == 0:


                #숏 시장가 주문!
                data = bybitX.create_market_sell_order(Target_Coin_Ticker, test_amt)


                #해당 코인 가격을 가져온다.
                coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)

                #예로 1% 상승한 가격에 지정가 주문으로 숏 포지션 종료하려면..
                target_price = coin_price * (1.0 - target_rate)
                            

                #롱 포지션 지정가 종료 주문!!                 
                print(bybitX.create_limit_buy_order(Target_Coin_Ticker, test_amt, target_price, {'reduce_only': True,'close_on_trigger':True}))

                stop_price = coin_price * (1.0 + target_rate)
                

                #스탑로스!
                myBybit.SetStopLossShortPrice(bybitX,Target_Coin_Ticker,stop_price)


            else:
                #숏 포지션이 있는 경우
                if abs(amt_s) > 0:

                    #숏 수익율을 구한다!
                    revenue_rate_s = (entryPrice_s - coin_price) / entryPrice_s * 100.0

                    print("revenue_rate_s : ", revenue_rate_s)




    except Exception as e:
        print("---:", e)



