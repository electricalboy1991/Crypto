import ccxt
import time
import pandas as pd
import pprint
       
import myBinance
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert #라인 메세지를 보내기 위함!

import json

'''
5분봉을 보지만 1분마다 돌도록 크론탭에 등록할 수 있습니다.
시간 정보를 읽어서 5분봉일때 필요한 동작을 하고
1분마다 돌때 또 필요한 동작을 하면 됩니다.

어떤 분봉 혹은 일봉을 볼지는 테스트 해보세요 ^^!


제가 알아내지 못한 버그나 오류가 있을 수도 있으니
이상하거나 문의가 있다면 클래스 영상에 댓글로 언제든지 알려주세요!
'''

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
Invest_Rate = 0.1


#테스트를 위해 비트코인만 일단 체크해봅니다. 
#LovelyCoinList = ['BTC/USDT']

#매매 대상 코인 개수 
CoinCnt = 5.0 #len(LovelyCoinList)


#나중에 5개의 코인만 해당 전략으로 매매하기 위해 이를 저장할 리스트를 선언합니다.
DolPaCoinList = list()

#파일 경로입니다.
dolpha_type_file_path = "/var/Autobot_seoul/BinanceRSIDolPaCoin.json"
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(dolpha_type_file_path, 'r') as json_file:
        DolPaCoinList = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("DolPaCoinList Exception by First")






#익절과 거미줄까는데 기준이된 변동성 값을 파일에 저장해 놓는다
ChangeValueDict = dict()

#파일 경로입니다.
change_value_file_path = "/var/Autobot_seoul/BinanceRSIchangeValue.json"
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(change_value_file_path, 'r') as json_file:
        ChangeValueDict = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("ChangeValueDict Exception by First")







###################################################
#설정할 레버리지!
set_leverage = 10



#선물 테더(USDT) 마켓에서 거래중인 코인을 거래대금이 많은 순서로 가져옵니다. 여기선 Top 25
TopCoinList = myBinance.GetTopCoinList(binanceX,25)

#비트코인과 이더리움을 제외 하고 싶다면이렇게 하면 됩니다!
#try - except로 감싸주는게 좋습니다. 왜냐하면 비트와 이더가 탑 25위 안에 안드는 일은 없겠지만
#다른 코인을 제외했는데 그 코인이 거래대금이 줄어들어 TopCoinList에서 빠지면
#리스트에서 없는 요소를 제거하려고 했기때문에 예외가 발생하고 아래 로직이 실행되지 않게 됩니다.


# try:
#     TopCoinList.remove("BTC/USDT")
#     TopCoinList.remove("ETH/USDT")
# except Exception as e:
#     print("Exception", e)


for ticker1 in Tickers:
    if "/USDT" in ticker1:
        candidate_ticker = ticker1
        if abs(float(Tickers[candidate_ticker]['info']['priceChangePercent'])) > 10:
            try:
                TopCoinList.remove(candidate_ticker)
            except Exception as e:
                print("Exception", e)


print(TopCoinList)

#잔고 데이타 가져오기 
balance = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)
#pprint.pprint(balance)

#시간 정보를 가져옵니다. 아침 9시의 경우 서버에서는 hour변수가 0이 됩니다.
time_info = time.gmtime()
hour = time_info.tm_hour
min = time_info.tm_min
print(hour, min)


#모든 선물 거래가능한 코인을 가져온다.
for ticker in Tickers:

    try: 

        if "/USDT" in ticker:
            Target_Coin_Ticker = ticker

            #러블리 코인이 아니라면 스킵! 러블리 코인만 대상으로 한다!!
            #즉 현재는 비트코인만 체크하게 됩니다.
            #if myBinance.CheckCoinInList(LovelyCoinList,ticker) == False:
            #    continue


            #탑코인 리스트에 속하거나 추세선 돌파에 의해 매매된 코인이라면...
            if myBinance.CheckCoinInList(TopCoinList,ticker) == True or myBinance.CheckCoinInList(DolPaCoinList,ticker) == True:


            
                time.sleep(0.2)
                print("Target_Coin_Ticker" , Target_Coin_Ticker)

                

                Target_Coin_Symbol = ticker.replace("/", "")


                time.sleep(0.05)
                #최소 주문 수량을 가져온다 
                minimun_amount = myBinance.GetMinimumAmount(binanceX,Target_Coin_Ticker)

                print("--- Target_Coin_Ticker:", Target_Coin_Ticker ," minimun_amount : ", minimun_amount)




                print(balance['USDT'])
                print("Total Money:",float(balance['USDT']['total']))
                print("Remain Money:",float(balance['USDT']['free']))


                leverage = 0  #레버리지

                #해당 코인 가격을 가져온다.
                coin_price = myBinance.GetCoinNowPrice(binanceX, Target_Coin_Ticker)





                #해당 코인에 할당된 금액에 따른 최대 매수수량을 구해본다!
                Max_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker, myBinance.GetAmount(float(balance['USDT']['total']),coin_price,Invest_Rate / CoinCnt)))  * set_leverage 
    
                print("Max_Amt:", Max_Amt)

                # 첫 진입 2 
                # 물타기는 4, 8, 16 으로 2배씩 거미줄을 깔 예정
                # 2 + 4 + 8 + 16 = 30
                # 따라서 첫 집입읍 2/30 = 1/15

                ###############################################################
                #어디까지나 예시로 첫 진입 수량과 물탈 수량은 자유롭게 여러분들이 설정하세요!!!!
                ###############################################################


                #코인별 할당된 수량의 절반으로 매수합니다. 
                Buy_Amt = Max_Amt / 3.0
                Buy_Amt = float(binanceX.amount_to_precision(Target_Coin_Ticker,Buy_Amt))

                #최소 주문 수량보다 작다면 이렇게 셋팅!
                if Buy_Amt < minimun_amount:
                    Buy_Amt = minimun_amount

                
                print("Final Buy_Amt:", Buy_Amt)


                #거미줄깔 맥스 수량!!
                Max_Water_Amt = Max_Amt - Buy_Amt




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
                








                #전략에 의해 매수 했는데..
                if myBinance.CheckCoinInList(DolPaCoinList,ticker) == True:
                    if min % 60 ==0:
                        line_alert.SendMessage("평가 금액 : " + str(balance['USDT']['total']))

                    #그런데 포지션이 없다. 익절이나 손절한 상태!
                    if abs(amt_s) == 0 and abs(amt_b) == 0:

                        #남은 주문읠 모두 취소하고
                        binanceX.cancel_all_orders(Target_Coin_Ticker)
                        time.sleep(0.1)

                        # 파일에서 제거해줘서 포지션을 잡을 수 있는 상태로 만든다!
                        DolPaCoinList.remove(Target_Coin_Ticker)
                                
                        #파일에 리스트 정보를 반영합니다!
                        with open(dolpha_type_file_path, 'w') as outfile:
                            json.dump(DolPaCoinList, outfile)


                        line_alert.SendMessage("RSI Divergence End!!!!! : " + Target_Coin_Ticker )


                        
                    else:

                        #주문 정보를 읽어온다.
                        orders = binanceX.fetch_orders(Target_Coin_Ticker)

                        #롱포지션이 있다면 현재 라이브상태!
                        if abs(amt_b) > 0:


                            #익절할 가격을 구합니다. 파일에 저장된 값 (change_value) 을 사용하는 것을 볼 수 있습니다!
                            target_price = entryPrice_b + (ChangeValueDict[Target_Coin_Ticker] * 1.0)

                                
                            #### 영상에 없지만 익절 주문이 있는지 여부 플래그 변수를 하나 만들었어요! ###
                            bExist = False


                            #주문 정보를 읽어온다.
                            for order in orders:
                                #익절 주문을 필터합니다.
                                if order['status'] == "open" and order['info']['positionSide'] == "LONG" and order['side'] == "sell" and order['type'] == "limit":

                                    bExist = True #### 익절 주문이 있다면 (당연히 있겠죠)! True를 입력해줍니다. ###
                                                
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
                                        #print(binanceX.create_limit_sell_order(Target_Coin_Ticker,abs(amt_b),target_price,params))
                                        print(binanceX.create_order(Target_Coin_Ticker, 'limit', 'sell', abs(amt_b), target_price, params))


                                        
                                        #아래 주석을 풀면 거미줄이 체결되 익절 주문이 변경될때 나에게 알림을 보낼 수 있습니다!
                                        line_alert.SendMessage("[바이_div_long물타기] : "  + Target_Coin_Ticker )


                            #### 앗 그런데 익절 주문이 없다고???? ###
                            if bExist == False:

                                #그럼 익절 주문을 걸어 둡니다     
                                params = {
                                    'positionSide': 'LONG'
                                }
                                #print(binanceX.create_limit_sell_order(Target_Coin_Ticker,abs(amt_b),target_price,params))
                                print(binanceX.create_order(Target_Coin_Ticker, 'limit', 'sell', abs(amt_b), target_price, params))
                                
                                   

                        #숏포지션이 있다면 현재 라이브상태!
                        if abs(amt_s) > 0:

                            #익절할 가격을 구합니다. 파일에 저장된 값 (change_value) 을 사용하는 것을 볼 수 있습니다!
                            target_price = entryPrice_s - (ChangeValueDict[Target_Coin_Ticker] * 1.0)
                                
                            #### 영상에 없지만 익절 주문이 있는지 여부 플래그 변수를 하나 만들었어요! ###
                            bExist = False

            
                            for order in orders:

                                #익절 주문을 필터합니다.
                                if order['status'] == "open" and order['info']['positionSide'] == "SHORT" and order['side'] == "buy" and order['type'] == "limit":
                                    
                                    pprint.pprint(order)
                                    bExist = True #### 익절 주문이 있다면 (당연히 있겠죠)! True를 입력해줍니다. ###
                                    
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
                                        #print(binanceX.create_limit_buy_order(Target_Coin_Ticker,abs(amt_s),target_price,params))
                                        print(binanceX.create_order(Target_Coin_Ticker, 'limit', 'buy', abs(amt_s), target_price, params))
    
                                        
                                        line_alert.SendMessage("[바이_div_short물타기]  : " + Target_Coin_Ticker )

                            #### 앗 그런데 익절 주문이 없다고???? ###
                            if bExist == False:

                                #그럼 익절 주문을 걸어 둡니다             
                                params = {
                                    'positionSide': 'SHORT'
                                }
                                #print(binanceX.create_limit_buy_order(Target_Coin_Ticker,abs(amt_s),target_price,params))
                                print(binanceX.create_order(Target_Coin_Ticker, 'limit', 'buy', abs(amt_s), target_price, params))



                else:

                
                    # 일봉 혹은 1분봉 취향에 맞게 변경해보세요!
                    #########################################################################
                    # 높은 타임 프레임으로 갈수록 다이버전스의 신뢰도는 높아집니다!
                    # 이 봇은 테스트용으로 5분마다 돌리는 것이며 장기적으로 수익이 날지 손실 이 날지 모릅니다!!
                    #########################################################################
                    # 5분마다 아래 로직이 실행된다!
                    if min % 5 == 0:


                        #캔들 정보 가져온다 - 5분봉 
                        df = myBinance.GetOhlcv(binanceX,Target_Coin_Ticker, '5m')

                        

                        #변동성의 절반! 이걸로 익절 손절 하자!
                        change_value = (float(df['high'][-2]) - float(df['low'][-2])) * 0.5


                        #단 변동성이 현재 코인가격의 0.25%보다 작다면 맞춰준다!
                        if change_value < coin_price * 0.0025:
                            change_value = coin_price * 0.0025

                        


                        #첫번째 꺾인 지점 (전저점)
                        up_first_point = 0
                        up_first_value = 0

                        #두번째 꺾인 지점 (전전저점)
                        up_second_point = 0
                        up_second_value = 0

                        #현재 RSI지표
                        now_rsi = myBinance.GetRSI(df,14,-1)

                
                        #전저, 전전저점 구해서 상승 추세선을 구할수 있으니 구해보자!
                        for index in range(3,20): #20개로 짧게 봅니다

                            left = myBinance.GetRSI(df,14,-(index-1))
                            middle = myBinance.GetRSI(df,14,-(index))
                            right = myBinance.GetRSI(df,14,-(index+1))


                            #꺾인 지점을 체크한다 
                            if left > middle < right:

                                # 이 안에 들어왔다는 이야기는 꺾인 지점을 발견한거다!!!
                                # 즉 꺾인 지점이닷!!!

                                if up_first_point == 0: #첫번째 꺾인 지점이 아직 셋팅 안되었다면 

                                    if now_rsi > middle: #그 지점이 현재가보다 작다면 

                                        #당첨!! 첫번째 꺾인 지점을 저장해 놓는다!
                                        up_first_point = index #캔들 번호 
                                        up_first_value = middle #캔들의 (종가)값

                                else: # 첫번째 꺾인 지점이 셋팅되어 0이 아니다! 그럼 두번째 꺾인 지점을 셋팅할 차례!

                                    if up_second_point == 0: # 두번째 꺾인 지점이 아직 셋팅 안되었다?

                                        #첫번째 꺾인 지점보다 가격이 낮을때만 두번째 지점을 셋팅한다!
                                        if up_first_value > middle:

                                            #위 조건을 만족했다면 두번째 지점 셋팅!!
                                            up_second_point = index
                                            up_second_value = middle

                                            #탈출!! 추세선을 그을 수 있는 저점 두 개를 찾았다!
                                            break

                        print("----------------------------------------------------------------------")
                        print("----------------------------------------------------------------------")
                        print("----------------------------------------------------------------------")
                                                
                        #실제 두 개의 좌표를 프린트 해봅니다.                         
                        print("up_first_point X:", up_first_point , " Y:" ,up_first_value)
                        print("up_second_point X:", up_second_point ," Y:" ,up_second_value)


                        IsLongDivergence = False

                        #영상에 빠졌지만 두 개의 좌표 값을 찾았을 때만 유효하게 합니다!
                        if up_first_point != 0 and up_second_point != 0:

                            if abs(amt_b) == 0 and df['close'][-(up_first_point)] < df['close'][-(up_second_point)] and len(DolPaCoinList) < CoinCnt:

                                #RSI지표가 두좌표중 1개가 35이하일때만 유효하게 하자!
                                if (up_first_value <= 35.0 or up_second_value <= 35.0) and now_rsi <35.0:
                                # if up_first_value <= 35.0 or up_second_value <= 35.0:
                                    IsLongDivergence = True
            





                        #첫번째 꺾인 지점 (전고점)
                        down_first_point = 0
                        down_first_value = 0

                        #첫번째 꺾인 지점 (전전고점)
                        down_second_point = 0
                        down_second_value = 0


                        #전고, 전전고점 구해서 하락 추세선을 구할수 있으니 구해보자!
                        for index in range(3,20): #20개로 짧게 봅니다


                            left = myBinance.GetRSI(df,14,-(index-1))
                            middle = myBinance.GetRSI(df,14,-(index))
                            right = myBinance.GetRSI(df,14,-(index+1))

                            #꺾인 지점을 체크한다 
                            if left < middle > right:


                                # 이 안에 들어왔다는 이야기는 꺾인 지점을 발견한거다!!!
                                # 즉 꺾인 지점이닷!!!

                                if down_first_point == 0: #첫번째 꺾인 지점이 아직 셋팅 안되었다면 

                                    if now_rsi < middle: #그 지점이 현재가보다 높다면 

                                        #당첨!! 첫번째 꺾인 지점을 저장해 놓는다!
                                        down_first_point = index #캔들 번호 
                                        down_first_value = middle #캔들의 (종가)값

                                else:  # 첫번째 꺾인 지점이 셋팅되어 0이 아니다! 그럼 두번째 꺾인 지점을 셋팅할 차례!
                                    
                                    if down_second_point == 0: # 두번째 꺾인 지점이 아직 셋팅 안되었다?

                                        #첫번째 꺾인 지점보다 가격이 높을 때만 두번째 지점을 셋팅한다!
                                        if down_first_value < middle:

                                            #위 조건을 만족했다면 두번째 지점 셋팅!!
                                            down_second_point = index
                                            down_second_value = middle

                                            #탈출!! 추세선을 그을 수 있는 저점 두 개를 찾았다!
                                            break

                        #실제 두 개의 좌표를 프린트 해봅니다.      
                        print("down_first_point X:", down_first_point , " Y:" ,down_first_value)
                        print("down_second_point X:", down_second_point ," Y:" ,down_second_value)

                        IsShortDivergence = False

                        #영상에 빠졌지만 두 개의 좌표 값을 찾았을 때만 유효하게 합니다!
                        if down_first_point != 0 and down_second_point != 0:

                            #다이버전스 발견!
                            if abs(amt_s) == 0 and df['close'][-(down_first_point)] > df['close'][-(down_second_point)] and len(DolPaCoinList) < CoinCnt:


                                #RSI지표가 두좌표중 1개가 65이상일때만 유효하게 하자!
                                if (down_first_value >= 65.0 or down_second_value >= 65.0) and now_rsi>=65.0:
                                # if down_first_value >= 65.0 or down_second_value >= 65.0:
                                    IsShortDivergence = True





                        #롱포지션을 잡을 수 있다! 하락 추세선을 위로 돌파한 상황!
                        if IsLongDivergence == True and IsShortDivergence == False:
                            #롱 포지션을 잡습니다.
                            params = {
                                'positionSide': 'LONG'
                            }
                            #data = binanceX.create_market_buy_order(Target_Coin_Ticker,Buy_Amt,params)
                            data = binanceX.create_order(Target_Coin_Ticker, 'market', 'buy', Buy_Amt, None, params)


                            #익절할 가격을 구합니다.
                            target_price = data['price'] + change_value
                            #그리고 지정가로 익절 주문을 걸어놓는다!            
                            #print(binanceX.create_limit_sell_order(Target_Coin_Ticker,data['amount'],target_price,params))
                            print(binanceX.create_order(Target_Coin_Ticker, 'limit', 'sell', data['amount'], target_price, params))

                            #아래는 물타기 라인을 긋는 로직입니다.
                            TotalWater_Amt = 0 #누적 거미줄에 깔린 수량

                            Water_amt = Buy_Amt

                            print("Water_amt", Water_amt)

                            i = 1
                

                            line_data = None

                            while TotalWater_Amt + Water_amt <= Max_Water_Amt: 

                                print("--------------------->",i ,": Grid!!!")

                                #############################################################
                                #이 수치를 낮추면 거미줄을 더 많이 깔 수 있습니다!
                                #사실 2.0은 꾀 높은 수치여서 거미줄이 2~3개밖에 안깔린다는 단점이 있습니다.
                                #############################################################
                                Water_amt *= 2.0


                                #############################################################
                                #(change_value * 2.0) 이 수치를 조절해 간격을 늘리거나 줄일 수 있는데 장단점이 있습니다. 
                                #정답은 없습니다. 자유롭게 변경하고 테스트 해보세요!
                                water_price = data['price'] - ((change_value * 2.0) * float(i))
                                #############################################################

                                #실제 물타는 매수 라인 주문을 넣는다.
                                params = {
                                    'positionSide': 'LONG'
                                }
                                #line_data = binanceX.create_limit_buy_order(Target_Coin_Ticker,Water_amt,water_price,params)
                                line_data = binanceX.create_order(Target_Coin_Ticker, 'limit', 'buy', Water_amt, water_price, params)
                                

                                TotalWater_Amt += Water_amt

                                
                                i += 1

                                time.sleep(0.1)


                            #line_data 에는 while문을 빠져나오기전 주문 즉 마지막 거미줄 주문 정보가 들어있습니다!!

                            #스탑할 가격을 구합니다. 거미줄 다 깔고 그 다음 거미줄 깔 자리에 스탑로스를 걸어 둡니다!
                            #스탑 로스는 마지막 거미줄 보다 change_value * 2.0 만큼 아래에 겁니다.
                            stop_price = line_data['price'] - (change_value*2.0)
                            #실제로 스탑로스를 가격으로 겁니다!
                            myBinance.SetStopLossLongPrice(binanceX, Target_Coin_Ticker, stop_price, False)


                            ####################################################################
                            #익절과 거미줄까는데 기준이된 변동성 값을 파일에 저장해 놓는다
                            #시간이 흐르면 캔들이 바뀌고 기준이 된 변동성 값이 바뀔 것이기 때문에 저장해 둬야 한다!!
                            ChangeValueDict[Target_Coin_Ticker] = change_value
                            
                            with open(change_value_file_path, 'w') as outfile:
                                json.dump(ChangeValueDict, outfile)


                            ####################################################################
                            #실제로 리스트에 매수(포지션 잡았다고)했다고 해당 코인 이름(티커)를 저장해둔다!
                            DolPaCoinList.append(Target_Coin_Ticker)
                                    
                            
                            with open(dolpha_type_file_path, 'w') as outfile:
                                json.dump(DolPaCoinList, outfile)
                            ####################################################################
                            


                            line_alert.SendMessage("[바이_div_롱_진입] " + Target_Coin_Ticker + " X: " + str(up_first_point) + "/" + str(round(up_first_value,1)) +  " , " + str(up_second_point)+ "/" + str(round(up_second_value,1)))

                                                
                            #매수 했다면 한번 더 잔고 데이타 가져오기 
                            balance = binanceX.fetch_balance(params={"type": "future"})




                        #숏포지션을 잡을 수 있다! 상승 추세선을 아래로 돌파한 상황!
                        if IsShortDivergence == True and IsLongDivergence == False :

                            #숏 포지션을 잡습니다.
                            params = {
                                'positionSide': 'SHORT'
                            }
                            #data = binanceX.create_market_sell_order(Target_Coin_Ticker,Buy_Amt,params)
                            data = binanceX.create_order(Target_Coin_Ticker, 'market', 'sell', Buy_Amt, None, params)


                            #익절할 가격을 구합니다.
                            target_price = data['price'] - change_value
                            #그리고 지정가로 익절 주문을 걸어놓는다!            
                            #print(binanceX.create_limit_buy_order(Target_Coin_Ticker,data['amount'],target_price,params))
                            print(binanceX.create_order(Target_Coin_Ticker, 'limit', 'buy', data['amount'], target_price, params))




                            #아래는 물타기 라인을 긋는 로직입니다.
                            TotalWater_Amt = 0 #누적 거미줄에 깔린 수량

                            Water_amt = Buy_Amt

                            print("Water_amt", Water_amt)

                            i = 1
                
                            line_data = None

                            while TotalWater_Amt + Water_amt <= Max_Water_Amt: 

                                print("--------------------->",i ,": Grid!!!")

                                #############################################################
                                #이 수치를 낮추면 거미줄을 더 많이 깔 수 있습니다!
                                #사실 2.0은 꾀 높은 수치여서 거미줄이 2~3개밖에 안깔린다는 단점이 있습니다.
                                #############################################################
                                Water_amt *= 2.0


                                #############################################################
                                #(change_value * 2.0) 이 수치를 조절해 간격을 늘리거나 줄일 수 있는데 장단점이 있습니다. 
                                #정답은 없습니다. 자유롭게 변경하고 테스트 해보세요!
                                water_price = data['price'] + ((change_value * 2.0) * float(i))
                                #############################################################


                                #실제 물타는 매수 라인 주문을 넣는다.
                                params = {
                                    'positionSide': 'SHORT'
                                }
                                #line_data = binanceX.create_limit_sell_order(Target_Coin_Ticker,Water_amt,water_price,params)
                                line_data = binanceX.create_order(Target_Coin_Ticker, 'limit', 'sell', Water_amt, water_price, params)

                                TotalWater_Amt += Water_amt

                                

                                i += 1

                                time.sleep(0.1)



                            #line_data 에는 while문을 빠져나오기전 주문 즉 마지막 거미줄 주문 정보가 들어있습니다!!

                            #스탑할 가격을 구합니다. 거미줄 다 깔고 그 다음 거미줄 깔 자리에 스탑로스를 걸어 둡니다!
                            #스탑 로스는 마지막 거미줄 보다 change_value * 2.0 만큼 위에 겁니다.
                            stop_price = line_data['price'] + (change_value * 2.0)
                            #실제로 스탑로스를 가격으로 겁니다!
                            myBinance.SetStopLossShortPrice(binanceX, Target_Coin_Ticker, stop_price, False)


                            ####################################################################
                            #익절과 거미줄까는데 기준이된 변동성 값을 파일에 저장해 놓는다
                            #시간이 흐르면 캔들이 바뀌고 기준이 된 변동성 값이 바뀔 것이기 때문에 저장해 둬야 한다!!
                            ChangeValueDict[Target_Coin_Ticker] = change_value
                            
                            with open(change_value_file_path, 'w') as outfile:
                                json.dump(ChangeValueDict, outfile)


                            ####################################################################
                            #실제로 리스트에 매수(포지션 잡았다고)했다고 해당 코인 이름(티커)를 저장해둔다!
                            DolPaCoinList.append(Target_Coin_Ticker)
                                    

                            with open(dolpha_type_file_path, 'w') as outfile:
                                json.dump(DolPaCoinList, outfile)
                            ####################################################################

                            line_alert.SendMessage("[바이_div_숏_진입]" + Target_Coin_Ticker + " X: " + str(down_first_point) + "/" + str(round(down_first_value,1)) +  " , " + str(down_second_point) + "/" + str(round(down_second_value,1)))


                            #매수 했다면 한번 더 잔고 데이타 가져오기 
                            balance = binanceX.fetch_balance(params={"type": "future"})


    except Exception as e:
        print("Exception:", e)











