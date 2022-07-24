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
##################################################
#테스트를 위해 코인 1개만 일단 해보시는걸 추천드립니다!
#적당한 변동성을 지닌 MANA, SAND, LINK 등의 코인으로 테스트 해보세요!!!
##################################################
LovelyCoinList = ['SAND/USDT:USDT']


#매매 대상 코인 개수 
CoinCnt = len(LovelyCoinList)


#################################################################################################################
#설정할 레버리지!
set_leverage = 5
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$#



##################################################
#영상과는 다르게 목표수익율을 상향 시켰습니다!
#이어지는 거미줄 갭과 맞췄다는걸 체크하실 수 있습니다
##################################################
target_rate = 0.005   #목표 수익은 일단 0.5% 알아서 조절하세요!!!!
target_revenute = target_rate * 100.0

##################################################
#영상에서 0.0025로 0.25%가 갭이었는데 
#변동성이 심한 코인들이기에 0.005으로 간격을 0.5%씩으로 늘렸습니다.
#그리고 레버에 따라 그리고 거미줄 깔때 배수에 따라서
#간격을 너무 늘리면 거미줄이 다 소진되기 전에 청산이 일어날 수도 있습니다. 
#(극단적인 예로 레버 100배인데 거미줄이 2%마다 깔려있다면 거미줄 체결되기 전에 청산 되겠죠?)
#정답은 없습니다! 전략에 맞게 간격을 수정하세요!!
##################################################
st_water_gap_rate = 0.005 #0.5% --> 몇 퍼센트씩 아래에 물타기를 넣을건지,.  0.005이면 0.5%로 -0.5%, -1.0%, -1.5%, 이렇게 물타기 라인을 긋는다.






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
            pprint.pprint(balances)
            time.sleep(0.1)

                        
            print(balances['USDT'])
            print("Total Money:",float(balances['USDT']['total']))
            print("Remain Money:",float(balances['USDT']['free']))



            leverage = 0

            #해당 코인 가격을 가져온다.
            coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)





            #해당 코인에 할당된 금액에 따른 최대 매수수량을 구해본다!
            Max_Amt = float(bybitX.amount_to_precision(Target_Coin_Ticker, myBybit.GetAmount(float(balances['USDT']['total']),coin_price,Invest_Rate / CoinCnt)))  * set_leverage 
 
            print("Max_Amt:", Max_Amt)
    

            ##################################################################
            #할당된 수량을 최소 주문 수량으로 나누면 분할이 가능한 숫자가 나옵니다
            minimun_divid_num = Max_Amt / minimun_amount
            
    
            #금액이 허용하는 한도내에서 최대 200분할로 
            divid_num= 200

            #다만 이 분할하고자 하는 개수는 최대 minimun_divid_num 만큼만 가능하니
            #크다면 조정해야 합니다!
            #즉 200분할을 위해 200을 넣었어도 할당된 원금(Max_Amt)이 작다면 200분할이 되지 않고
            #최소 주문 수량 기준으로 분할된 숫자가 나오게 됩니다. (원금이 매우 작다면 200으로 설정했지만 50분할밖에 안 나올 수도 있습니다!)
            if divid_num > minimun_divid_num:
                divid_num = minimun_divid_num

            ##################################################################




            #100분할 해서 1회 매수 코인 수량으로 정한다!
            Buy_Amt = Max_Amt / divid_num
            Buy_Amt = float(bybitX.amount_to_precision(Target_Coin_Ticker,Buy_Amt))

            
            print("Buy_Amt:", Buy_Amt)

            #최소 주문 수량보다 작다면 이렇게 셋팅!
            if Buy_Amt < minimun_amount:
                Buy_Amt = minimun_amount

            

            #################################
            #롱 숏 각각 거미줄들에 할당할 맥스 수량!
            #최대 할당 수량에서 첫 진입한 수량 1개씩 총 2개를 빼주면 총 물탈 수량이 나오는데
            #이를 롱과 숏이 나눠가져야 되니깐 2로 나누면 됩니다!
            Max_Water_Amt = (Max_Amt - (Buy_Amt * 2.0)) / 2.0
            #################################
            

            



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
                    pprint.pprint(posi)
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


            

            #둘다 포지션이 없을때만 신규로 포지션 진입한다
            if amt_s == 0 and amt_b == 0:

                ##########################################################################
                #영상에 빠져있지만 양방향 모두 남아있는 주문을 취소하고 새로 포지션 잡고 거미줄을 깔아야합니다.
                ##########################################################################
                myBybit.CancelAllOrder(bybitX, Target_Coin_Ticker)
                time.sleep(0.1)



                FirstAmt = Buy_Amt


                
                ##########################################################################
                #롱 포지션 잡고 거미줄을 깝니다.
                ##########################################################################

                #롱 포지션을 잡습니다.
                data = bybitX.create_market_buy_order(Target_Coin_Ticker, FirstAmt)
                #해당 코인 가격을 가져온다.
                coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)



                #아래는 물타기 라인을 긋는 로직입니다.
                TotalWater_Amt = 0 #누적 거미줄에 깔린 수량

                Water_amt = FirstAmt

                if Water_amt < Buy_Amt:
                    Water_amt = Buy_Amt

                i = 1


                while TotalWater_Amt + Water_amt < Max_Water_Amt:

                    print("--------------------->",i ,": Grid!!!")

                    water_price = coin_price * (1.0 - (st_water_gap_rate * i)) 



                    #실제 물타는 매수 라인 주문을 넣는다.
                    print(bybitX.create_limit_buy_order(Target_Coin_Ticker, Water_amt, water_price))

                    TotalWater_Amt += Water_amt

                    Water_amt *= 1.05

                    i += 1

                    time.sleep(0.1)





                ##########################################################################
                #숏 포지션 잡고 거미줄을 깝니다.
                ##########################################################################


                #숏 포지션을 잡습니다.
                data = bybitX.create_market_sell_order(Target_Coin_Ticker, FirstAmt)
                #해당 코인 가격을 가져온다.
                coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)


                #아래는 물타기 라인을 긋는 로직입니다.
                TotalWater_Amt = 0 #누적 거미줄에 깔린 수량

                Water_amt = FirstAmt

                if Water_amt < Buy_Amt:
                    Water_amt = Buy_Amt

                i = 1

                while TotalWater_Amt + Water_amt < Max_Water_Amt : 

                    print("--------------------->",i ,": Grid!!!")

                    water_price = coin_price * (1.0 + (st_water_gap_rate * i)) 



                    #실제 물타는 매수 라인 주문을 넣는다.
                    print(bybitX.create_limit_sell_order(Target_Coin_Ticker, Water_amt, water_price))
                    

                    TotalWater_Amt += Water_amt

                    Water_amt *= 1.05

                    i += 1

                    time.sleep(0.1)







            #포지션이 양쪽 다 잡혀있다.
            else:
                print("")

                #둘중 1개가 청산당했다면 익절도 동시에 해줘야 한다! - 청산빔이 나온다면 얼마든지 가능한 시나리오다
                if amt_s == 0 and abs(amt_b) > 0:

                    #주문 취소후
                    myBybit.CancelAllOrder(bybitX, Target_Coin_Ticker)
                    time.sleep(0.1)


                    print(bybitX.create_market_sell_order(Target_Coin_Ticker, abs(amt_b), {'reduce_only': True,'close_on_trigger':True}))

                        
                    line_alert.SendMessage(Target_Coin_Ticker + " ByBit Cut Loss by Short!!")
                    continue


                if amt_b == 0 and abs(amt_s) > 0:


                    #주문 취소후
                    myBybit.CancelAllOrder(bybitX, Target_Coin_Ticker)
                    time.sleep(0.1)
     

                    print(bybitX.create_market_buy_order(Target_Coin_Ticker, abs(amt_s), {'reduce_only': True,'close_on_trigger':True}))


                    line_alert.SendMessage(Target_Coin_Ticker + " ByBit Cut Loss by Long!!")
                    continue



                unrealizedProfit_s = 0 #미 실현 손익.
                unrealizedProfit_b = 0 #미 실현 손익.
 

                #숏 잔고
                for posi in balances2:
                    if posi['info']['symbol'] == Target_Coin_Symbol and posi['info']['side'] == "Sell":
                        unrealizedProfit_s = float(posi['info']['unrealised_pnl'])
                        break

                #롱 잔고
                for posi in balances2:
                    if posi['info']['symbol'] == Target_Coin_Symbol and posi['info']['side'] == "Buy":
                        unrealizedProfit_b = float(posi['info']['unrealised_pnl'])
                        break



                #해당 코인 가격을 가져온다.
                coin_price = myBybit.GetCoinNowPrice(bybitX, Target_Coin_Ticker)

                
                #숏 수익율을 구한다!
                revenue_rate_s = (entryPrice_s - coin_price) / entryPrice_s * 100.0


                #롱 수익율을 구한다!
                revenue_rate_b = (coin_price - entryPrice_b) / entryPrice_b * 100.0



                #수수료를 감안해 각각 0.7과 1.3을 곱해서 보정을 한다!
                unrealizedProfit_s_f = float(unrealizedProfit_s) * 0.70
                if float(unrealizedProfit_s) < 0:
                    unrealizedProfit_s_f = float(unrealizedProfit_s) * 1.3



                unrealizedProfit_b_f = float(unrealizedProfit_b) * 0.70
                if float(unrealizedProfit_b) < 0:
                    unrealizedProfit_b_f = float(unrealizedProfit_b) * 1.3


                
                ori_total_profit = float(unrealizedProfit_s) + float(unrealizedProfit_b)
                total_profit = float(unrealizedProfit_s_f) + float(unrealizedProfit_b_f)

                print("---- ori_total_profit", ori_total_profit)
                print("---- total_profit", total_profit)

                #수익이 나왔다!
                if total_profit > 0 and ( (abs(amt_b) <= abs(amt_s) and  revenue_rate_s >= target_revenute) or (abs(amt_b) >= abs(amt_s) and  revenue_rate_b >= target_revenute) ) :
   

                    ##########################################################################
                    #두 포지션 모두 종료 합니다.
                    ##########################################################################

                    print(bybitX.create_market_sell_order(Target_Coin_Ticker, abs(amt_b), {'reduce_only': True,'close_on_trigger':True}))

                        
                    print(bybitX.create_market_buy_order(Target_Coin_Ticker, abs(amt_s), {'reduce_only': True,'close_on_trigger':True}))
                    
                    time.sleep(0.5)

                    ##########################################################################
                    #영상에 빠져있지만 양방향 모두 남아있는 주문을 취소해줍니다 
                    ##########################################################################
                    myBybit.CancelAllOrder(bybitX, Target_Coin_Ticker)
                    time.sleep(0.1)

                    line_alert.SendMessage(Target_Coin_Ticker + " ByBit Bot End!!" )

                else:
                    #아직 수익이 나오지 않은 상태! 여기서는 1 : 4 로 맞춰주기 위해서 물린쪽 포지션 수량의 0.25를 곱했습니다.
                    # 1:5로 하려면 0.2 등을 입력해야 되니 영상과는 다르게 변수를 만들어 처리했습니다.

                    ###############################
                    #비율 변수 
                    TRate = 0.25
                    ###############################

                    #롱의 물량이 더 많다 즉 물린 상태 
                    if abs(amt_b) > abs(amt_s):
                        
                        #지정된 비율, 여기선 1:4 비율이 아니라면 이익이나는 물량이 적은 쪽 포지션의 수량을 더해서 맞춰줍니다.
                        if abs(amt_b) * TRate > abs(amt_s):
                            Add_Amt = abs(amt_b) * TRate - abs(amt_s)

                            if Add_Amt >= minimun_amount:
                                #숏 포지션을 추가로 잡습니다.
                                print(bybitX.create_market_sell_order(Target_Coin_Ticker, FirstAmt))

                                line_alert.SendMessage(Target_Coin_Ticker + " ByBit Add Amt!! Short " )


                    #숏이 물량이 더 많다 즉 물린 상태 
                    if abs(amt_b) < abs(amt_s):

                        #지정된 비율, 여기선 1:4 비율이 아니라면 이익이나는 물량이 적은 쪽 포지션의 수량을 더해서 맞춰줍니다.
                        if abs(amt_s) * TRate > abs(amt_b):
                            Add_Amt = abs(amt_s) * TRate - abs(amt_b)

                            if Add_Amt >= minimun_amount:
                                #롱 포지션을 추가로 잡습니다.
                                print(bybitX.create_market_buy_order(Target_Coin_Ticker, FirstAmt))

                                line_alert.SendMessage(Target_Coin_Ticker + " ByBit Add Amt!! Long " )
            



    except Exception as e:
        print("---:", e)



