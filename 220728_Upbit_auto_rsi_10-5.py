#-*-coding:utf-8 -*-
import myUpbit   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit

import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert   

import json

'''
15분봉을 보지만 1분마다 혹은 3분마다 돌도록 크론탭에 등록할 수 있습니다.
시간 정보를 읽어서 15분봉일때 필요한 동작을 하고
1분마다 혹은 3분마다 돌때 또 필요한 동작을 하면 됩니다.

업비트 거래대금 탑 코인 리스트를 파일로 빠르게 읽는 방법 :
https://blog.naver.com/zacra/222670663136

위 과정을 진행안해서 탑코인 구하는 로직이 느리다면 3분마다 돌리시는걸 권장합니다!

어떤 분봉 혹은 일봉을 볼지는 테스트 해보세요 ^^!

제가 알아내지 못한 버그나 오류가 있을 수도 있으니
이상하거나 문의가 있다면 클래스 영상에 댓글로 언제든지 알려주세요!
'''

####################################
#필요하지 않다면 주석처리하세요!!!
# time.sleep(25.0)
####################################

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myUpbit.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Upbit_AccessKey = simpleEnDecrypt.decrypt(my_key.upbit_access)
Upbit_ScretKey = simpleEnDecrypt.decrypt(my_key.upbit_secret)

#업비트 객체를 만든다
upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)


#내가 매수할 총 코인 종류 개수
MaxCoinCnt = 2.0

#내가 가진 잔고 데이터를 다 가져온다.
balances = upbit.get_balances()

#TotalMoney = myUpbit.GetTotalMoney(balances) #총 원금

#내 남은 원화(현금))을 구한다.
TotalWon = float(upbit.get_balance("KRW"))

######################################################
#이런식으로 해당 전략에 할당할 금액을 조절할 수도 있습니다.
#이 경우 내가 가진 원화의 30%를 맥스로 해서 매매합니다!
#자금 사정과 전략에 맞게 조절하세요!!!
TotalWon = TotalWon * 0.3
######################################################



###############################################################
#어디까지나 예시로 첫 진입 금액과 물탈 금액은 자유롭게 여러분들이 설정하세요!!!!
###############################################################


#코인당 할당된 매수금액
CoinMoney = TotalWon / MaxCoinCnt

# 첫 진입 2 
# 물타기는 4, 8, 16 으로 2배씩 거미줄을 깔 예정
# 2 + 4 + 8 + 16 = 30
# 따라서 첫 집입읍 2/30 = 1/15

#할당 금액의 1/15 을 첫 진입 금액으로!
FirstEnterMoney = CoinMoney / 15.0

#5천원 이하면 매수가 아예 안되니 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
if FirstEnterMoney < 5000:
    FirstEnterMoney = 5000

#물탈 총 금액
WaterMaxMoney = CoinMoney - FirstEnterMoney

###############################################################
###############################################################




print("-----------------------------------------------")
print ("CoinMoney:", CoinMoney)
print ("FirstEnterMoney:", FirstEnterMoney)
print ("WaterTotalMoney:", WaterMaxMoney)


#거미줄 간격 1.5%! 영상에서는 1%였는데 조금 늘려봤습니다 ^^! 
st_water_gap_rate = 0.015


#목표 수익 0.5%!
target_rate = 0.01 # 0.5%.. 전략에 맞게 조절 하세용~



#빈 리스트를 선언합니다.
DolPaCoinList = list()

#파일 경로입니다.
dolpha_type_file_path = "/var/Autobot_seoul/UpbitRSIDolPaCoin.json"
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다.
    with open(dolpha_type_file_path, 'r') as json_file:
        DolPaCoinList = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First")









#########################################################
#거래대금이 많은 탑코인 30개의 리스트
'''
TopCoinList = myUpbit.GetTopCoinList("day",30)


현재 위에처럼 가져오면 느리니
아래 과정을 통해 개선해보세요!

업비트 거래대금 탑 코인 리스트를 파일로 빠르게 읽는 방법 :
https://blog.naver.com/zacra/222670663136
#(업비트 베스트 봇 과정인데 이 1탄 만 보시고 적용하셔도 됩니다)
'''
#
# Tickers = pyupbit.get_tickers("KRW")
# #########################################################
#
#
# top_file_path = "./UpbitTopCoinList.json"
#
# TopCoinList = list()
#
# #파일을 읽어서 리스트를 만듭니다.
# try:
#     with open(top_file_path, "r") as json_file:
#         TopCoinList = json.load(json_file)
#
# except Exception as e:
#     TopCoinList = myUpbit.GetTopCoinList("day",20)
#     print("Exception by First")
#
#




#구매 제외 코인 리스트 - 필요없다면 비워두세요
#OutCoinList = []
# OutCoinList = ['KRW-LTC','KRW-BTC','KRW-ETH','KRW-ADA','KRW-DOT','KRW-AVAX','KRW-SOL','KRW-MATIC','KRW-ALGO','KRW-MANA','KRW-LINK','KRW-BAT','KRW-ATOM']


LovelyCoinList = ['KRW-BTC','KRW-ETH']

#시간 정보를 가져옵니다. 아침 9시의 경우 서버에서는 hour변수가 0이 됩니다.
time_info = time.gmtime()
hour = time_info.tm_hour
min = time_info.tm_min
print(hour, min)



for ticker in LovelyCoinList:
    try: 
        print("Coin Ticker: ",ticker)

        # #구매 제외 코인 들은 어떠한 매매도 하지 않는다!!
        # if myUpbit.CheckCoinInList(OutCoinList,ticker) == True:
        #     continue

        time.sleep(0.1)


        #전략에 의해 매수 했고
        if myUpbit.CheckCoinInList(DolPaCoinList,ticker) == True:


            #따라서 잔고도 있다.
            if myUpbit.IsHasCoin(balances, ticker) == True:


                #수익율 구하기..
                revenu_rate = myUpbit.GetRevenueRate(balances,ticker)
                print("---Revenue-->", revenu_rate)


                #코인의 평균 단가
                avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)

                #수익 목표가
                target_price =  avgPrice * (1.0 + target_rate)

                #지정가 주문 데이터를 읽는다.
                orders_data = upbit.get_order(ticker)

                #모든 주문을 뒤진다!
                for order in orders_data:

                    if order['side'] == 'ask' : #매도 주문인데
                        # 거미줄이 깔리면 수량과 평단이 계속 바뀌니까.. 업데이트 해줘야지
                        if float(order['price']) != float(pyupbit.get_tick_size(target_price)): #현재 평단기준으로 구한 목표 가격과 즉 익절 라인 같지 않다면 갱신해야 한다!

                            upbit.cancel_order(order['uuid']) #해당 주문 취소 시키고! 다시 새 주문을 거다

                            time.sleep(0.2)

                            #해당 코인의 현재 보유 수량
                            coin_volume = upbit.get_balance(ticker)

                            #지정가 매도를 주문을 다시 넣는다(익절)
                            myUpbit.SellCoinLimit(upbit,ticker,target_price,coin_volume)

                ####################################################################################
                #만약? 손절이 필요하다? 그러신 분은 주석 해제 하고 적절하게 사용하세요~^^!
                # if revenu_rate < -10.0:
                #     #시장가로 모두 매도!
                #     balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))
                ####################################################################################

            else:


                #잔고가 없다면 익절이나 손절된 상태니깐 파일에서 지워주자!!
                DolPaCoinList.remove(ticker)

                #파일에 리스트를 저장합니다
                with open(dolpha_type_file_path, 'w') as outfile:
                    json.dump(DolPaCoinList, outfile)


                #기존에 걸린 지정가 주문들을 취소한다.
                myUpbit.CancelCoinOrder(upbit,ticker)


                line_alert.SendMessage("[업빗_rsi_div봇_수익]!!!!! : " + ticker )


        #아직 전략에 의해 매수되지 않음
        else:

            #일봉 혹은 5분봉 취향에 맞게 변경해보세요!
            #15분마다 아래 로직이 실행된다!
            #이 봇을 1분 3분 기준으로 돌릴거기 때문에
            if min % 5 == 0:


                time.sleep(0.2)
                df = pyupbit.get_ohlcv(ticker,interval="minute15") #여기선 15분봉 데이타를 가져온다.



                #첫번째 꺾인 지점 (전저점)
                up_first_point = 0
                up_first_value = 0

                #두번째 꺾인 지점 (전전저점)
                up_second_point = 0
                up_second_value = 0

                #현재 RSI지표
                now_rsi = myUpbit.GetRSI(df,14,-1)



                # 전저, 전전저점 구해서 상승 추세선을 구할수 있으니 구해보자!
                # 데이터 개수를 20개로 한정했습니다!
                # 너무 긴 다이버젼스를 봐선 안됨

                for index in range(3,20):

                    left = myUpbit.GetRSI(df,14,-(index-1))
                    middle = myUpbit.GetRSI(df,14,-(index))
                    right = myUpbit.GetRSI(df,14,-(index+1))


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


                #RSI 상승 추세선은 up_first_value > up_second_value

                IsLongDivergence = False

                #영상엔 빠져있지만 두 개의 점을 모두 다 찾았을 때만 유효하다!
                if up_first_point != 0 and up_second_point != 0:

                    #다이버전스 발생!
                    if df['close'][-(up_first_point)] <= df['close'][-(up_second_point)]:

                        #RSI지표가 두좌표중 1개가 35이하일때만 유효하게 하자!
                        if (up_first_value <= 35.0 or up_second_value <= 35.0) and now_rsi<=35:

                            IsLongDivergence = True


                #다이버전스가 발견 되었다면!
                if IsLongDivergence == True:

                    #현재 해당 전략에 의해 매수된 코인 개수가 맥스 코인보다 적다면! 매수한다!
                    if len(DolPaCoinList) < MaxCoinCnt and myUpbit.IsHasCoin(balances, ticker) == False:

                        line_alert.SendMessage("!다이버젼스 발생! : " + ticker + " --> " + str(round(up_first_point,2)) + " " + str(round(up_second_point,2)))

                        #시장가 매수를 한다.
                        balances = myUpbit.BuyCoinMarket(upbit,ticker,FirstEnterMoney)

                        #평균매입단가와 매수개수를 구해서 목표한 수익율로 지정가 매도주문을 걸어놓는다.
                        avgPrice = myUpbit.GetAvgBuyPrice(balances,ticker)
                        coin_volume = upbit.get_balance(ticker)

                        target_price =  avgPrice * (1.0 + target_rate) # 익절 라인 목표 가격

                        #지정가 매도를 주문을 넣는다(익절)
                        myUpbit.SellCoinLimit(upbit,ticker,target_price,coin_volume)




                        #아래는 물타기 라인을 긋는 로직이다.
                        Water_Money = FirstEnterMoney #필요한 돈을 구한다.

                        #누적 거미줄에 깔린 금액
                        TotalWater_Money = 0

                        i = 1
                        while TotalWater_Money + Water_Money <= WaterMaxMoney:

                            water_price = avgPrice * (1.0 - (st_water_gap_rate * i)) # 1% 하락한 지점의 가격
                            Water_Money *= 2.0 #필요한 금액은 2배씩 늘어난다.

                            #그럼 그 금액으로 얼마큼의 수량을살 수 있느냐?
                            water_volume = Water_Money / water_price #필요 금액에서 타겟 가격을 나누면 된다

                            #실제 물타는 매수 라인 주문을 넣는다.
                            myUpbit.BuyCoinLimit(upbit,ticker,water_price,water_volume)
                            time.sleep(0.2)

                            TotalWater_Money += Water_Money

                            i += 1




                        #매수된 코인을 DolPaCoinList 리스트에 넣고 이를 파일로 저장해둔다!
                        DolPaCoinList.append(ticker)

                        #파일에 리스트를 저장합니다
                        with open(dolpha_type_file_path, 'w') as outfile:
                            json.dump(DolPaCoinList, outfile)



    except Exception as e:
        print("---:", e)



