import pyupbit
import time
import pandas as pd



#한글은 서버에서 돌리면 깨지니 참고하세요 



#챕터7까지 진행하시면서 봇은 점차 완성이 되어 갑니다!!!
#챕터5까지 완강 후 봇을 돌리셔도 되지만 이왕이면 7까지 완강하신 후 돌리시는 걸 추천드려요!
access = "15XXj7UPGD5dkBQK4zeFJMuqjQeEce9P6MuPIRdIhhzKUDCFuZoQsvjfKiP2sRaY"          # 본인 값으로 변경
secret = "tjJlMeq25x4aOdThgq3DHr5bHhtkmZIOBLTMiulht2NBlTQbH0H0EA4FaznwNYtK"          # 본인 값으로 변경

upbit = pyupbit.Upbit(access, secret)

#아래 함수안의 내용은 참고로만 보세요! 제가 말씀드렸죠? 검증된 함수니 안의 내용 몰라도 그냥 가져다 쓰기만 하면 끝!
#RSI지표 수치를 구해준다. 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetRSI(ohlcv,period,st):
    #이 안의 내용이 어려우시죠? 넘어가셔도 되요. 우리는 이 함수가 RSI지표를 정확히 구해준다는 것만 알면 됩니다.
    ohlcv["close"] = ohlcv["close"]
    delta = ohlcv["close"].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
    RS = _gain / _loss
    return float(pd.Series(100 - (100 / (1 + RS)), name="RSI").iloc[st])

#이동평균선 수치를 구해준다 첫번째: 분봉/일봉 정보, 두번째: 기간, 세번째: 기준 날짜
def GetMA(ohlcv,period,st):
    #이 역시 이동평균선을 제대로 구해줍니다.
    close = ohlcv["close"]
    ma = close.rolling(period).mean()
    return float(ma[st])

#거래대금이 많은 순으로 코인 리스트를 얻는다. 첫번째 : Interval기간(day,week,minute15 ....), 두번째 : 몇개까지 
def GetTopCoinList(interval,top):
    print("--------------GetTopCoinList Start-------------------")
    #원화 마켓의 코인 티커를 리스트로 담아요.
    Tickers = pyupbit.get_tickers("KRW")

    #딕셔너리를 하나 만듭니다.
    dic_coin_money = dict()

    #for문을 돌면서 모든 코인들을 순회합니다.
    for ticker in Tickers:
        try:
            #캔들 정보를 가져와서 
            df = pyupbit.get_ohlcv(ticker,interval)
            #최근 2개 캔들의 종가와 거래량을 곱하여 대략의 거래대금을 구합니다.
            volume_money = (df['close'][-1] * df['volume'][-1]) + (df['close'][-2] * df['volume'][-2])
            #volume_money = float(df['value'][-1]) + float(df['value'][-2]) #거래대금!
            #이걸 위에서 만든 딕셔너리에 넣어줍니다. Key는 코인의 티커, Value는 위에서 구한 거래대금 
            dic_coin_money[ticker] = volume_money
            #출력해 봅니다.
            print(ticker, dic_coin_money[ticker])
            #반드시 이렇게 쉬어줘야 합니다. 안그럼 에러가.. 시간조절을 해보시며 최적의 시간을 찾아보세요 전 일단 0.1로 수정했어요!
            time.sleep(0.1)

        except Exception as e:
            print("exception:",e)

    #딕셔너리를 값으로 정렬하되 숫자가 큰 순서대로 정렬합니다.
    dic_sorted_coin_money = sorted(dic_coin_money.items(), key = lambda x : x[1], reverse= True)

    #빈 리스트를 만듭니다.
    coin_list = list()

    #코인을 셀 변수를 만들어요.
    cnt = 0

    #티커와 거래대금 많은 순으로 정렬된 딕셔너리를 순회하면서 
    for coin_data in dic_sorted_coin_money:
        #코인 개수를 증가시켜주는데..
        cnt += 1

        #파라메타로 넘어온 top의 수보다 작으면 코인 리스트에 코인 티커를 넣어줍니다.
        #즉 top에 10이 들어갔다면 결과적으로 top 10에 해당하는 코인 티커가 coin_list에 들어갑니다.
        if cnt <= top:
            coin_list.append(coin_data[0])
        else:
            break

    print("--------------GetTopCoinList End-------------------")

    #코인 리스트를 리턴해 줍니다.
    return coin_list

#해당되는 리스트안에 해당 코인이 있는지 여부를 리턴하는 함수
def CheckCoinInList(CoinList,Ticker):
    InCoinOk = False

    #리스트안에 해당 코인이 있는지 체크합니다.
    for coinTicker in CoinList:
        #있으면 True로!!
        if coinTicker == Ticker:
            InCoinOk = True
            break

    return InCoinOk

#티커에 해당하는 코인의 수익율을 구해서 리턴하는 함수.
def GetRevenueRate(balances,Ticker):
    revenue_rate = 0.0
    for value in balances:
        try:
            realTicker = value['unit_currency'] + "-" + value['currency']
            if Ticker == realTicker:
                time.sleep(0.05)
                
                #현재 가격을 가져옵니다.
                nowPrice = pyupbit.get_current_price(realTicker)

                #수익율을 구해서 넣어줍니다
                revenue_rate = (float(nowPrice) - float(value['avg_buy_price'])) * 100.0 / float(value['avg_buy_price'])
                break

        except Exception as e:
            print("GetRevenueRate error:", e)

    return revenue_rate

#티커에 해당하는 코인의 총 매수금액을 리턴하는 함수
def GetCoinNowMoney(balances,Ticker):
    CoinMoney = 0.0
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            #해당 코인을 지정가 매도를 걸어놓으면 그 수량이 locked에 잡히게 됩니다. 
            #만약 전체 수량을 지정가 매도를 걸었다면 balance에 있던 잔고가 모두 locked로 이동하는 거죠
            #따라서 총 코인 매수 금액을 구하려면 balance + locked를 해줘야 합니다.
            CoinMoney = float(value['avg_buy_price']) * (float(value['balance']) + float(value['locked']))
            break
    return CoinMoney

#티커에 해당하는 코인이 매수된 상태면 참을 리턴하는함수
def IsHasCoin(balances,Ticker):
    HasCoin = False
    for value in balances:
        realTicker = value['unit_currency'] + "-" + value['currency']
        if Ticker == realTicker:
            HasCoin = True
    return HasCoin

#내가 매수한 (가지고 있는) 코인 개수를 리턴하는 함수
def GetHasCoinCnt(balances):
    CoinCnt = 0
    for value in balances:
        avg_buy_price = float(value['avg_buy_price'])
        if avg_buy_price != 0: #원화, 드랍받은 코인(평균매입단가가 0이다) 제외!
            CoinCnt += 1
    return CoinCnt

#총 원금을 구한다!
def GetTotalMoney(balances):
    total = 0.0
    for value in balances:
        try:
            ticker = value['currency']
            if ticker == "KRW": #원화일 때는 평균 매입 단가가 0이므로 구분해서 총 평가금액을 구한다.
                total += (float(value['balance']) + float(value['locked']))
            else:
                avg_buy_price = float(value['avg_buy_price'])

                #매수평균가(avg_buy_price)가 있으면서 잔고가 0이 아닌 코인들의 총 매수가격을 더해줍니다.
                if avg_buy_price != 0 and (float(value['balance']) != 0 or float(value['locked']) != 0):
                    #balance(잔고 수량) + locked(지정가 매도로 걸어둔 수량) 이렇게 해야 제대로 된 값이 구해집니다.
                    #지정가 매도 주문이 없다면 balance에 코인 수량이 100% 있지만 지정가 매도 주문을 걸면 그 수량만큼이 locked로 옮겨지기 때문입니다.
                    total += (avg_buy_price * (float(value['balance']) + float(value['locked'])))
        except Exception as e:
            print("GetTotalMoney error:", e)
    return total

#총 평가금액을 구한다! 
#위 원금을 구하는 함수와 유사하지만 코인의 매수 평균가가 아니라 현재 평가가격 기준으로 총 평가 금액을 구한다.
def GetTotalRealMoney(balances):
    total = 0.0
    for value in balances:

        try:
            ticker = value['currency']
            if ticker == "KRW": #원화일 때는 평균 매입 단가가 0이므로 구분해서 총 평가금액을 구한다.
                total += (float(value['balance']) + float(value['locked']))
            else:
            
                avg_buy_price = float(value['avg_buy_price'])
                if avg_buy_price != 0 and (float(value['balance']) != 0 or float(value['locked']) != 0): #드랍받은 코인(평균매입단가가 0이다) 제외 하고 현재가격으로 평가금액을 구한다,.
                    realTicker = value['unit_currency'] + "-" + value['currency']

                    time.sleep(0.1)
                    nowPrice = pyupbit.get_current_price(realTicker)
                    total += (float(nowPrice) * (float(value['balance']) + float(value['locked'])))
        except Exception as e:
            print("GetTotalRealMoney error:", e)


    return total


#내가 매수할 총 코인 개수
MaxCoinCnt = 5.0

#처음 매수할 비중(퍼센트)
FirstRate = 10.0
#추가 매수할 비중 (퍼센트)
WaterRate = 5.0

#내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()

TotalMoeny = GetTotalMoney(balances) #총 원금
TotalRealMoney = GetTotalRealMoney(balances) #총 평가금액

#내 총 수익율
TotalRevenue = (TotalRealMoney - TotalMoeny) * 100.0/ TotalMoeny

#코인당 매수할 최대 매수금액
CoinMaxMoney = TotalMoeny / MaxCoinCnt


#처음에 매수할 금액 
FirstEnterMoney = CoinMaxMoney / 100.0 * FirstRate 

#그 이후 매수할 금액 
WaterEnterMoeny = CoinMaxMoney / 100.0 * WaterRate

print("-----------------------------------------------")
print ("총 투자 원금: ", GetTotalMoney(balances))
print ("현재 평가 금액: ", GetTotalRealMoney(balances))
print ("총 수익율: ", TotalRevenue)
print("-----------------------------------------------")
print ("코인당 최대 매수 금액 : ", CoinMaxMoney)
print ("처음 매수할 금액 : ", FirstEnterMoney)
print ("추가매수(물탈) 금액 : ", WaterEnterMoeny)


#거래대금이 많은 탑코인 10개의 리스트
TopCoinList = GetTopCoinList("week",10)

#구매 제외 코인 리스트
OutCoinList = ['KRW-MARO','KRW-TSHP','KRW-PXL','KRW-BTC']

#나의 코인
LovelyCoinList = ['KRW-BTC','KRW-ETH','KRW-DOGE','KRW-DOT']


Tickers = pyupbit.get_tickers("KRW")


for ticker in Tickers:
    try: 
        print("코인 티커 : ",ticker)
        #거래량 많은 탑코인 리스트안의 코인이 아니라면 스킵! 탑코인에 해당하는 코인만 이후 로직을 수행한다.
        if CheckCoinInList(TopCoinList,ticker) == False:
            continue
        #위험한 코인이라면 스킵!!!
        if CheckCoinInList(OutCoinList,ticker) == True:
            continue
        #나만의 러블리만 사겠다! 그 이외의 코인이라면 스킵!!!
        #if CheckCoinInList(LovelyCoinList,ticker) == False:
        #    continue

        print("!!!!! 내 전략에 맞는 매수매도 대상 코인 :",ticker)
        
        time.sleep(0.05)
        df_60 = pyupbit.get_ohlcv(ticker,interval="minute60") #60분봉 데이타를 가져온다.

        #RSI지표를 구한다.
        #제가 현재 캔들을 -1 이 아니라 -2로 
        #이전 캔들을 -2가 아니라 -3으로 수정했습니다. 이유는 아래 이어지는 주석의 내용을 참고하세요!
        rsi60_min_before = GetRSI(df_60,14,-3)
        rsi60_min = GetRSI(df_60,14,-2)

    
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################

        #반드시 이 글을 읽고 수정하세요 https://blog.naver.com/zacra/222567868086
        # 지표를 활용할 때 현재 캔들 -1 과 이전 캔들 -2는 값이 같아지는 경우가 생길 수 있습니다. 
        # (봇이 캔들이 변경되는 시점에 주로 실행되기에 이 경우 현재 캔들 기준으로 구한 지표 값과 이전 캔들 기준으로 구한 지표 값이 동일해 지는 상황압니다,)
        # 따라서 이전 캔들 -2, 이이전 캔들 -3으로 조합해야 원하는 결과를 얻을 수 있습니다.
        # 쉽게 이야기해서 현재 캔들을 -2, 이전 캔들을 -3으로 보는게 좋다는 거죠. 어자피 진짜 현재 캔들 -1과 이전 캔들 -2의 값이 보통 같을테니까요. 
        # (이전 캔들의 종가와 현재 캔들의 시가가 거의 같은 경우가 많으니까요!)

        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        #################################################################################################################
        
        #수익율을 구한다.
        revenu_rate = GetRevenueRate(balances,ticker)


        time.sleep(0.05)
        #원화 잔고를 가져온다
        won = float(upbit.get_balance("KRW"))
        print("# 현재 남은 돈(원화) :", won)

        print("------------------------------------")
        print("코인 ticker :",ticker)
        print("- 최근 RSI지표 추이 :", rsi60_min_before, " -> ", rsi60_min)
        print("- 현재 수익율 : ",revenu_rate)
       

        #이미 매수된 코인이다. 물타기!!
        if IsHasCoin(balances,ticker) == True:


            #현재 코인의 총 매수금액
            NowCoinTotalMoney = GetCoinNowMoney(balances,ticker)

            #60분봉 기준 RSI지표 70 이상이면서 수익권일때 분할 매도를 한다.
            if rsi60_min >= 70.0 and revenu_rate >= 1.0:
                print("!!!!!!!!!!!!!!!수익 성공 야호  분할 매도!!!!!!!!!!!!!!!!!!!!")

                #최대코인매수금액의 1/4보다 작다면 전체 시장가 매도 
                if NowCoinTotalMoney < (CoinMaxMoney / 4.0):
                    print(upbit.sell_market_order(ticker,upbit.get_balance(ticker)))
                #최대코인매수금액의 1/4보다 크다면 절반씩 시장가 매도 
                else:
                    print(upbit.sell_market_order(ticker,upbit.get_balance(ticker) / 2.0))

                time.sleep(2.0)
                #팔았으면 원화를 다시 가져올 필요가 있다.
                won = float(upbit.get_balance("KRW"))
               



            #내가 가진 원화가 물탈 돈보다 적다..(원금 바닥) 그런데 수익율이 - 10% 이하다? 그럼 절반 팔아서 물탈돈을 마련하자!
            if won < WaterEnterMoeny and revenu_rate <= -10.0:
                print("!!!!!!!!!!!!!!!원화 바닥 해당 코인 절반 매도합니다 ㅜ.ㅜ !!!!!!!!!!!!!!!!!!!!")
                print(upbit.sell_market_order(ticker,upbit.get_balance(ticker) / 2.0))
      


            #할당된 최대코인매수금액 대비 매수된 코인 비율
            Total_Rate = NowCoinTotalMoney / CoinMaxMoney * 100.0

            #60분봉 기준 RSI지표 30 이하에서 빠져나왔을 때
            if rsi60_min_before <= 30.0 and rsi60_min > 30.0:
                #할당된 최대코인매수금액 대비 매수된 코인 비중이 50%이하일때..
                if Total_Rate <= 50.0:
                    print("!!!!!!!!!!!!!!!물탈 돈으로 물을 탑니다!!!!!!!!!!!!!!!!!!!!!")
                    time.sleep(0.05)
                    print(upbit.buy_market_order(ticker,WaterEnterMoeny))
                #50%를 초과하면
                else:
                    print("!!!!!!!!!!!!!!! 수익율이 ",revenu_rate,"일때만 물을 탑니다 !!!!!!!!!!!!!!!!!!!!!")
                    #수익율이 마이너스 5% 이하 일때만 매수를 진행하여 원금 소진을 늦춘다.
                    if revenu_rate <= -5.0:
                        print("!!!!!!!!!!!!!!!물탈 돈으로 물을 탑니다!!!!!!!!!!!!!!!!!!!!!")
                        time.sleep(0.05)
                        print(upbit.buy_market_order(ticker,WaterEnterMoeny))

        #아직 매수안한 코인
        else:
            #60분봉 기준 RSI지표 30 이하이면서 아직 매수한 코인이 MaxCoinCnt보다 작다면 매수 진행!
            #if rsi60_min <= 30.0 and GetHasCoinCnt(balances) < MaxCoinCnt :

            #60분봉 기준 RSI지표 30 이하에서 빠져나오면서 아직 매수한 코인이 MaxCoinCnt보다 작다면 매수 진행!
            if rsi60_min_before <= 30.0 and rsi60_min > 30.0 and GetHasCoinCnt(balances) < MaxCoinCnt :
                print("!!!!!!!!!!!!!!!첫 매수! 가즈아!!!!!!!!!!!!!!!!!!!!!!!!")
                time.sleep(0.05)
                print(upbit.buy_market_order(ticker,FirstEnterMoney))

    except Exception as e:
        print("error:", e)



























