import ccxt
import time
import pandas as pd
import pprint
       
import myBinance
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert #라인 메세지를 보내기 위함!

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)


#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
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





#선물 마켓에서 거래중인 모든 코인을 가져옵니다.
Tickers = binanceX.fetch_tickers()


#총 원금대비 설정 비율 
#아래처럼 0.2 로 셋팅하면 20%가 해당 전략에 할당된다는 이야기!
Invest_Rate = 0.2


#!!!여기에 매매 대상 코인을 넣으세요.!!!
#변동성이 높아서 아래의 코인들을 선택함 !!
LovelyCoinList = ['GMT/USDT','APE/USDT']

#매매 대상 코인 개수 
CoinCnt = len(LovelyCoinList)


#################################################################################################################
#설정할 레버리지!
#여기서 레버 20배 쓴 이유는, 많은 돈으로 거미줄을 많이 깔기 위함임
#아마 기본 거래 수량 맞추기 위해서 일 듯
set_leverage = 20


target_rate = 0.003   #목표 수익은 일단 0.3% 알아서 조절하세요!!!!
target_revenute = target_rate * 100.0

#0.25% --> 몇 퍼센트씩 아래에 물타기를 넣을건지,.  0.0025이면 0.25%로 -0.25%, -0.5%, -0.75%, -1% 이렇게 물타기 라인을 긋는다.
#거미줄 간격임
st_water_gap_rate = 0.0025
line_number = 20 #물타기 라인 개수 
#################################################################################################################


#선물 테더(USDT) 마켓에서 거래중인 코인을 거래대금이 많은 순서로 가져옵니다. 여기선 Top 25
#TopCoinList = myBinance.GetTopCoinList(binanceX,25)



#모든 선물 거래가능한 코인을 가져온다.
#사실 내가 원하는 코인만 for문 돌릴거라면,
#for ticker in LovelyCoinList: 이렇게 하고 돌려도 됨
for ticker in Tickers:

    try: 

   
        #하지만 여기서는 USDT 테더로 살수 있는 모든 선물 거래 코인들을 대상으로 돌려봅니다.
        if "/USDT" in ticker:
            Target_Coin_Ticker = ticker

            #러블리 코인이 아니라면 스킵! 러블리 코인만 대상으로 한다!!
            if myBinance.CheckCoinInList(LovelyCoinList,ticker) == False:
                continue

           
            
            time.sleep(0.2)

            Target_Coin_Symbol = ticker.replace("/", "")


            time.sleep(0.05)
            #최소 주문 수량을 가져온다 
            minimun_amount = myBinance.GetMinimumAmount(binanceX,Target_Coin_Ticker)

            print("--- Target_Coin_Ticker:", Target_Coin_Ticker ," minimun_amount : ", minimun_amount)



            #잔고 데이타 가져오기 
            balance = binanceX.fetch_balance(params={"type": "future"})
            time.sleep(0.1)
            #pprint.pprint(balance)


            print(balance['USDT'])
            print("Total Money:",float(balance['USDT']['total']))
            print("Remain Money:",float(balance['USDT']['free']))


            leverage = set_leverage  #레버리지

            #해당 코인 가격을 가져온다.
            coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)



            #해당 코인에 할당된 금액에 따른 최대 매수수량을 구해본다!
            #amount_to_precision 매매가 가능한 수량으로 변경해줌
            #Invest_Rate 내가 원금대비 얼만큼의 투자를 할 지 비율
            #Invest_Rate / CoinCnt 각각 갯수에 맞게 나눠가져야지
            Max_Amt = float(binanceX.amount_to_precision
                            (Target_Coin_Ticker, myBinance.GetAmount(float(balance['USDT']['total']),coin_price,Invest_Rate / CoinCnt)))  * leverage
 
            print("Max_Amt:", Max_Amt)
    

            #100분할 해서 1회 매수 코인 수량으로 정한다!
            #거미줄 갯수?
            Buy_Amt = Max_Amt / 100.0
            Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker,Buy_Amt))

            
            print("Buy_Amt:", Buy_Amt)

            #최소 주문 수량보다 작다면 이렇게 셋팅!
            if Buy_Amt < minimun_amount:
                Buy_Amt = minimun_amount

            
            print("Final Buy_Amt:", Buy_Amt)




            amt_s = 0 
            amt_b = 0
            entryPrice_s = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
            entryPrice_b = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.


            isolated = True #격리모드인지 



            print("------")
            #숏잔고
            for posi in balance['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                    print(posi)
                    amt_s = float(posi['positionAmt'])
                    entryPrice_s= float(posi['entryPrice'])
                    leverage = float(posi['leverage'])
                    isolated = posi['isolated']
                    break


            #롱잔고
            for posi in balance['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'LONG':
                    print(posi)
                    amt_b = float(posi['positionAmt'])
                    entryPrice_b = float(posi['entryPrice'])
                    leverage = float(posi['leverage'])
                    isolated = posi['isolated']
                    break





            #################################################################################################################
            #레버리지 셋팅
            if leverage != set_leverage:
                    
                try:
                    print(binanceX.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                except Exception as e:
                    print("Exception:", e)

            #################################################################################################################


            #################################################################################################################
            #격리 모드로 설정
            if isolated == False:
                try:
                    print(binanceX.fapiPrivate_post_margintype({'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
                except Exception as e:
                    print("Exception:", e)
            #################################################################################################################    

  
            #숏 포지션이 존재하지 않으면
            if amt_s == 0:

                #영상엔 없지만 포지션 잡을때 마다 내게 메세지를 보내봅니다! (이게 오면 익절했다는 이야기겠죠?) 자꾸 오는게 싫으시면 주석처리 하시면 됩니다!
                line_alert.SendMessage(Target_Coin_Ticker + " Grid Short Start!! " )


                #주문 정보를 읽어서 혹시 걸려있는 주문이 있다면 모두 취소해준다! 새로 숏포지션 잡고 거미줄 새로 깔꺼니깐
                orders = binanceX.fetch_orders(Target_Coin_Ticker)

                for order in orders:

                    #그냥 숏에 오픈된 주문 전체를 취소하는 것으로 변경했습니다!
                    #open된 주문이 있냐는 거임
                    if order['status'] == "open"  and order['info']['positionSide'] == "SHORT":
                        binanceX.cancel_order(order['id'],Target_Coin_Ticker)

                        #영상에 빠뜨렸지만 이렇게 꼭 쉬어줘야 합니다!
                        time.sleep(0.05)

                #숏 포지션을 잡습니다.
                params = {
                    'positionSide': 'SHORT'
                }
                data = binanceX.create_market_sell_order(Target_Coin_Ticker, Buy_Amt,params)


                #익절할 가격을 구합니다.
                target_price = data['price'] * (1.0 - target_rate)


                #그리고 지정가로 익절 주문을 걸어놓는다!            
                params = {
                    'positionSide': 'SHORT'
                }
                print(binanceX.create_limit_buy_order(Target_Coin_Ticker, data['amount'],  target_price ,params))


                #아래는 물타기 라인을 긋는 로직입니다. 거미줄 치는 로직
                #Buy_Amt는 코인에 할당된 금액의 100분할
                Water_amt = Buy_Amt
                print("Water_amt", Water_amt)

                for i in range(1,line_number+1): #st_water_gap_rate가 0.0025이라면 손실율 -0.25,-0.5,-0.75, 에 물타기 라인을 근다. 
                    print("--------------------->",i ,": Grid!!!")

                    water_price = data['price'] * (1.0 + (st_water_gap_rate * i)) # 0.25%씩 가격이 상승합니다.
      
                    #실제 물타는 매수 라인 주문을 넣는다.
                    params = {
                        'positionSide': 'SHORT'
                    }
                    print(binanceX.create_limit_sell_order(Target_Coin_Ticker, Water_amt,  water_price ,params))

                    time.sleep(0.1)
            else:

                #포지션이 잡힌 상태다.
                if abs(amt_s) > 0:

                    #익절할 가격을 구합니다.
                    target_price = entryPrice_s * (1.0 - target_rate)


                    #주문 정보를 읽어온다.
                    orders = binanceX.fetch_orders(Target_Coin_Ticker)
                    for order in orders:

                        #익절 주문을 필터합니다.
                        if order['status'] == "open" and order['info']['positionSide'] == "SHORT" and order['side'] == "buy":
                            #이 안에 들어왔다면 익절 주문인데
                            #익절 주문의 가격이 위에서 방금 구한 익절할 가격과 다르다면? 거미줄에 닿아 평단과 수량이 바뀐 경우니깐 
                            if float(order['price']) != float(binanceX.price_to_precision(Target_Coin_Ticker,target_price)):

                                #기존 익절 주문 취소하고
                                binanceX.cancel_order(order['id'],Target_Coin_Ticker)

                                time.sleep(0.1)

                                #다시 익절 지정가 주문을 걸어 놓습니다!
                                params = {
                                    'positionSide': 'SHORT'
                                }
                                print(binanceX.create_limit_buy_order(Target_Coin_Ticker, abs(amt_s), target_price ,params))




            #롱 포지션이 존재하지 않으면
            if amt_b == 0:

                #영상엔 없지만 포지션 잡을때 마다 내게 메세지를 보내봅니다! (이게 오면 익절했다는 이야기겠죠?) 자꾸 오는게 싫으시면 주석처리 하시면 됩니다!
                line_alert.SendMessage(Target_Coin_Ticker + " Grid Long Start!! " )

                #주문 정보를 읽어서 혹시 걸려있는 주문이 있다면 모두 취소해준다! 새로 롱포지션 잡고 거미줄 새로 깔꺼니깐
                orders = binanceX.fetch_orders(Target_Coin_Ticker)

                for order in orders:
                    #그냥 롱에 오픈된 주문 전체를 취소하는 것으로 변경했습니다!
                    if order['status'] == "open"  and order['info']['positionSide'] == "LONG":
                        binanceX.cancel_order(order['id'],Target_Coin_Ticker)

                        #영상에 빠뜨렸지만 이렇게 꼭 쉬어줘야 합니다!
                        time.sleep(0.05)



                #롱 포지션을 잡습니다.
                params = {
                    'positionSide': 'LONG'
                }
                data = binanceX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt,params)


                #익절할 가격을 구합니다.
                target_price = data['price'] * (1.0 + target_rate)
                            
                #그리고 지정가로 익절 주문을 걸어놓는다!        
                params = {
                    'positionSide': 'LONG'
                }
                print(binanceX.create_limit_sell_order(Target_Coin_Ticker, data['amount'] , target_price ,params))
                

                #아래는 물타기 라인을 긋는 로직입니다.
                Water_amt = Buy_Amt
                print("Water_amt", Water_amt)

                for i in range(1,line_number+1): #st_water_gap_rate가 0.0025이라면 손실율 -0.25,-0.5,-0.75, 에 물타기 라인을 근다. 
                    print("--------------------->",i ,": Grid!!!")

                    water_price = data['price'] * (1.0 - (st_water_gap_rate * i)) # 0.25%씩 가격이 하락합니다.
      

                    #실제 물타는 매수 라인 주문을 넣는다.
                    params = {
                        'positionSide': 'LONG'
                    }
                    print(binanceX.create_limit_buy_order(Target_Coin_Ticker, Water_amt, water_price,params))

                    time.sleep(0.1)

            else:
                #포지션이 잡힌 상태다.
                if abs(amt_b) > 0:

                    #익절할 가격을 구합니다.
                    target_price = entryPrice_b * (1.0 + target_rate)

                    #주문 정보를 읽어온다.
                    orders = binanceX.fetch_orders(Target_Coin_Ticker)

                    #주문 정보를 읽어온다.
                    for order in orders:
                        #익절 주문을 필터합니다.
                        if order['status'] == "open" and order['info']['positionSide'] == "LONG" and order['side'] == "sell":
                            #이 안에 들어왔다면 익절 주문인데
                            #익절 주문의 가격이 위에서 방금 구한 익절할 가격과 다르다면? 거미줄에 닿아 평단과 수량이 바뀐 경우니깐 
                            if float(order['price']) != float(binanceX.price_to_precision(Target_Coin_Ticker,target_price)):

                                #기존 익절 주문 취소하고
                                binanceX.cancel_order(order['id'],Target_Coin_Ticker)
                                
                                time.sleep(0.1)

                                #다시 익절 지정가 주문을 걸어 놓습니다!
                                params = {
                                    'positionSide': 'LONG'
                                }
                                print(binanceX.create_limit_sell_order(Target_Coin_Ticker, abs(amt_b) , target_price ,params))
                                


    except Exception as e:
        print("Exception:", e)








