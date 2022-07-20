import ccxt
import time
import pandas as pd
import pprint

import myBybit
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키


import line_alert #라인 메세지를 보내기 위함!

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




#총 원금대비 설정 비율 
#아래처럼 0.2 로 셋팅하면 20%가 해당 전략에 할당된다는 이야기!
Invest_Rate = 0.2


#!!!여기에 매매 대상 코인을 넣으세요.!!!
LovelyCoinList = ['GMT/USDT:USDT','APE/USDT:USDT']

#매매 대상 코인 개수 
CoinCnt = len(LovelyCoinList)


#################################################################################################################
#설정할 레버리지!
set_leverage = 20


target_rate = 0.003   #목표 수익은 일단 0.3% 알아서 조절하세요!!!!
target_revenute = target_rate * 100.0

st_water_gap_rate = 0.0025 #0.25% --> 몇 퍼센트씩 아래에 물타기를 넣을건지,.  0.0025이면 0.25%로 -0.25%, -0.5%, -0.75%, -1% 이렇게 물타기 라인을 긋는다.
line_number = 10 #물타기 라인 개수 
#################################################################################################################







#모든 선물 거래가능한 코인을 가져온다.
for ticker in Tickers:

    try: 

   
        #하지만 여기서는 USDT 테더로 살수 있는 모든 선물 거래 코인들을 대상으로 돌려봅니다.
        if "/USDT" in ticker:
            Target_Coin_Ticker = ticker

            #러블리 코인이 아니라면 스킵! 러블리 코인만 대상으로 한다!!
            if myBybit.CheckCoinInList(LovelyCoinList,ticker) == False:
                continue

            
            time.sleep(0.2)
            
            Target_Coin_Symbol = ticker.replace("/", "").replace(":USDT","")



            time.sleep(0.05)
            #최소 주문 수량을 가져온다 
            minimun_amount = myBybit.GetMinimumAmount(bybitX,Target_Coin_Symbol)

            print("--- Target_Coin_Ticker:", Target_Coin_Ticker ," minimun_amount : ", minimun_amount)





            #잔고 데이타 가져오기 
            balances = bybitX.fetch_balance(params={"type": "future"})
            time.sleep(0.1)

                        
            print(balances['USDT'])
            print("Total Money:",float(balances['USDT']['total']))
            print("Remain Money:",float(balances['USDT']['free']))



            leverage = set_leverage  #레버리지

            #해당 코인 가격을 가져온다.
            coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)





            #해당 코인에 할당된 금액에 따른 최대 매수수량을 구해본다!
            Max_Amt = float(bybitX.amount_to_precision(Target_Coin_Ticker, myBybit.GetAmount(float(balances['USDT']['total']),coin_price,Invest_Rate / CoinCnt)))  * leverage 
 
            print("Max_Amt:", Max_Amt)
    

            #100분할 해서 1회 매수 코인 수량으로 정한다!
            Buy_Amt = Max_Amt / 100.0
            Buy_Amt = float(bybitX.amount_to_precision(Target_Coin_Ticker,Buy_Amt))

            
            print("Buy_Amt:", Buy_Amt)

            #최소 주문 수량보다 작다면 이렇게 셋팅!
            if Buy_Amt < minimun_amount:
                Buy_Amt = minimun_amount

            
            print("Final Buy_Amt:", Buy_Amt)




            amt_s = 0 
            amt_b = 0
            entryPrice_s = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
            entryPrice_b = 0 #평균 매입 단가. 따라서 물을 타면 변경 된다.
            is_isolated = False

            #잔고 데이타 가져오기 
            balances2 = bybitX.fetch_positions(None, {'type':'Future'})
            time.sleep(0.1)


            #숏 잔고
            for posi in balances2:
                if posi['info']['symbol'] == Target_Coin_Symbol and posi['info']['side'] == "Sell":
                    amt_s = float(posi['info']['size'])
                    entryPrice_s = float(posi['info']['entry_price'])
                    leverage = float(posi['info']['leverage'])
                    is_isolated = posi['info']['is_isolated']
                    break

            #롱 잔고
            for posi in balances2:
                if posi['info']['symbol'] == Target_Coin_Symbol and posi['info']['side'] == "Buy":
                    amt_b = float(posi['info']['size'])
                    entryPrice_b = float(posi['info']['entry_price'])
                    leverage = float(posi['info']['leverage'])
                    is_isolated = posi['info']['is_isolated']
                    break


            #################################################################################################################
            #레버리지와 격리모드 셋팅합니다! 
            print("###############", leverage)

            #교차 모드로 했다가 다시 격리모드로 설정하는 이유는 이미 교차모드일 경우 레버리지만 변경할려는 경우 이미 교차여서 레버리지 수정이 안되는 현상이 발견되어
            #이렇게 교차모드와 레버리지 설정했다가 다시 격리모드로 설정하는 식으로 보완을 했습니다!
            if is_isolated == False or leverage != set_leverage:
                try:
                    print(bybitX.set_margin_mode("CROSS",Target_Coin_Symbol, {'leverage':set_leverage}))
                except Exception as e:
                    print("---:", e)

                try:
                    print(bybitX.set_margin_mode("ISOLATED",Target_Coin_Symbol, {'leverage':set_leverage}))
                except Exception as e:
                    print("---:", e)

            #################################################################################################################



            #숏 포지션이 없을 경우
            if abs(amt_s) == 0:

                #영상엔 없지만 포지션 잡을때 마다 내게 메세지를 보내봅니다! (이게 오면 익절했다는 이야기겠죠?) 자꾸 오는게 싫으시면 주석처리 하시면 됩니다!
                line_alert.SendMessage(Target_Coin_Ticker + " Grid Short Start!! " )


                #주문 정보를 읽어서 혹시 걸려있는 주문이 있다면 모두 취소해준다! 새로 숏포지션 잡고 거미줄 새로 깔꺼니깐
                orders = bybitX.fetch_orders(Target_Coin_Ticker,None,500)

                for order in orders:

                    #숏의 오픈 주문을 취소합니다.
                    if order['status'] == "open" and order['info']['close_on_trigger'] == False and order['side'] == "sell":
                        bybitX.cancel_order(order['id'],Target_Coin_Ticker)

                        #영상에 빠뜨렸지만 이렇게 꼭 쉬어줘야 합니다!
                        time.sleep(0.05)
         


                #숏 시장가 주문!
                data = bybitX.create_market_sell_order(Target_Coin_Ticker, Buy_Amt)
                #해당 코인 가격을 가져온다.
                coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)

                
                #익절할 가격을 구합니다.
                target_price = coin_price * (1.0 - target_rate)
                            

                #숏 포지션 지정가 종료 주문!!                 
                print(bybitX.create_limit_buy_order(Target_Coin_Ticker, Buy_Amt, target_price, {'reduce_only': True,'close_on_trigger':True}))



                

                #아래는 물타기 라인을 긋는 로직입니다.
                Water_amt = Buy_Amt
                print("Water_amt", Water_amt)

                for i in range(1,line_number+1): #st_water_gap_rate가 0.0025이라면 손실율 -0.25,-0.5,-0.75, 에 물타기 라인을 근다. 
                    print("--------------------->",i ,": Grid!!!")

                    water_price = coin_price * (1.0 + (st_water_gap_rate * i)) # 0.25%씩 가격이 하락합니다.
      

                    #실제 물타는 매수 라인 주문을 넣는다.
                    print(bybitX.create_limit_sell_order(Target_Coin_Ticker, Water_amt, water_price))

                    time.sleep(0.1)
                

            else:
                #숏 포지션이 있는 경우
                if abs(amt_s) > 0:


                    #익절할 가격을 구합니다.
                    target_price = entryPrice_s * (1.0 - target_rate)



                    orders = bybitX.fetch_orders(Target_Coin_Ticker,None,500)


                    for order in orders:

                        #익절 주문을 필터합니다.
                        if order['status'] == "open"  and order['info']['close_on_trigger'] == True and order['side'] == "buy":
                            #이 안에 들어왔다면 익절 주문인데
                            #익절 주문의 가격이 위에서 방금 구한 익절할 가격과 다르다면? 거미줄에 닿아 평단과 수량이 바뀐 경우니깐 
                            if float(order['price']) != float(bybitX.price_to_precision(Target_Coin_Ticker,target_price)):

                                #기존 익절 주문 취소하고
                                bybitX.cancel_order(order['id'],Target_Coin_Ticker)

                                time.sleep(0.1)

     
                                #숏 포지션 지정가 종료 주문!!                 
                                print(bybitX.create_limit_buy_order(Target_Coin_Ticker, abs(amt_s), target_price, {'reduce_only': True,'close_on_trigger':True}))



                    
            
            
            #롱 포지션이 없을 경우
            if abs(amt_b) == 0:

                #영상엔 없지만 포지션 잡을때 마다 내게 메세지를 보내봅니다! (이게 오면 익절했다는 이야기겠죠?) 자꾸 오는게 싫으시면 주석처리 하시면 됩니다!
                line_alert.SendMessage(Target_Coin_Ticker + " Grid Long Start!! " )


                #주문 정보를 읽어서 혹시 걸려있는 주문이 있다면 모두 취소해준다! 새로 롱포지션 잡고 거미줄 새로 깔꺼니깐
                orders = bybitX.fetch_orders(Target_Coin_Ticker,None,500)

                for order in orders:

                    #롱의 오픈 주문을 취소합니다.
                    if order['status'] == "open" and order['info']['close_on_trigger'] == False and order['side'] == "buy":
                        bybitX.cancel_order(order['id'],Target_Coin_Ticker)

                        #영상에 빠뜨렸지만 이렇게 꼭 쉬어줘야 합니다!
                        time.sleep(0.05)
         


                #롱 시장가 주문!
                data = bybitX.create_market_buy_order(Target_Coin_Ticker, Buy_Amt)
                
                #해당 코인 가격을 가져온다.
                coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)


                #익절할 가격을 구합니다.
                target_price = coin_price * (1.0 + target_rate)
                            

                #롱 포지션 지정가 종료 주문!!     
                print(bybitX.create_limit_sell_order(Target_Coin_Ticker, Buy_Amt, target_price, {'reduce_only': True,'close_on_trigger':True}))

                

                #아래는 물타기 라인을 긋는 로직입니다.
                Water_amt = Buy_Amt
                print("Water_amt", Water_amt)

                for i in range(1,line_number+1): #st_water_gap_rate가 0.0025이라면 손실율 -0.25,-0.5,-0.75, 에 물타기 라인을 근다. 
                    print("--------------------->",i ,": Grid!!!")

                    water_price = coin_price * (1.0 - (st_water_gap_rate * i)) # 0.25%씩 가격이 하락합니다.
      

                    #실제 물타는 매수 라인 주문을 넣는다.
                    print(bybitX.create_limit_buy_order(Target_Coin_Ticker, Water_amt, water_price))

                    time.sleep(0.1)



            else:
                #롱 포지션이 있는 경우
                if abs(amt_b) > 0:

                    #익절할 가격을 구합니다.
                    target_price = entryPrice_s * (1.0 + target_rate)



                    orders = bybitX.fetch_orders(Target_Coin_Ticker,None,500)


                    for order in orders:

                        #익절 주문을 필터합니다.
                        if order['status'] == "open"  and order['info']['close_on_trigger'] == True and order['side'] == "sell":
                            #이 안에 들어왔다면 익절 주문인데
                            #익절 주문의 가격이 위에서 방금 구한 익절할 가격과 다르다면? 거미줄에 닿아 평단과 수량이 바뀐 경우니깐 
                            if float(order['price']) != float(bybitX.price_to_precision(Target_Coin_Ticker,target_price)):

                                #기존 익절 주문 취소하고
                                bybitX.cancel_order(order['id'],Target_Coin_Ticker)

                                time.sleep(0.1)

     
                                #롱 포지션 지정가 종료 주문!!                 
                                print(bybitX.create_limit_sell_order(Target_Coin_Ticker, abs(amt_b), target_price, {'reduce_only': True,'close_on_trigger':True}))



            


    except Exception as e:
        print("---:", e)



