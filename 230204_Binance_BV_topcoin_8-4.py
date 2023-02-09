#-*-coding:utf-8 -*-
import myBinance   #우리가 만든 함수들이 들어있는 모듈
import time
import pyupbit
import ccxt
import ende_key  #암복호화키
import my_key    #업비트 시크릿 액세스키

import line_alert   

import json

import platform
'''

업비트 거래대금 탑 코인 리스트를 파일로 빠르게 읽는 방법 :
https://blog.naver.com/zacra/222670663136

이 부분을 적용한 봇입니다.
주석을 확인해보세요!


'''

#############################################################
# 파일 저장을 배우기 위한 샘플 예제로 수익을 담보하지 않으니 
# 여러가지 자신만의 전략을 보완하여 수정해 나가세요!
#############################################################

if platform.system() == 'Windows':
    pass
else:
    time.sleep(15)

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)

#시간 정보를 가져옵니다. 아침 9시의 경우 서버에서는 hour변수가 0이 됩니다.
time_info = time.gmtime()
hour = time_info.tm_hour
minute = time_info.tm_min
month = time_info.tm_mon

#내가 매수할 총 코인 개수
MaxCoinCnt = 8.0
k_parameter = 0.49
GetInMoney=50
set_leverage=1
average_noise = 0.5

if month ==11 or  month ==12 or  month ==1 or  month ==2 or  month ==3 or  month ==4:
    season_weight = 1.3
else:
    season_weight = 1.0

time.sleep(0.05)

# binance 객체 생성
binanceX = ccxt.binance(config={'apiKey': Binance_AccessKey,'secret': Binance_ScretKey,'enableRateLimit': True,'options': {'defaultType': 'future'}})

#잔고 데이타 가져오기
balance_binance = binanceX.fetch_balance(params={"type": "future"})
time.sleep(0.1)


#코인당 매수할 매수금액
CoinMoney = balance_binance['BUSD']['free'] / MaxCoinCnt

#5천원 이하면 매수가 아예 안되나 5천원 미만일 경우 강제로 5000원으로 만들어 준다!
if CoinMoney < 100:
    CoinMoney = 100

print("-----------------------------------------------")
print ("TotalWon:", balance_binance['BUSD']['free'])
print ("CoinMoney:", CoinMoney)




#파일 경로입니다.
if platform.system() == 'Windows':
    BV_file_path = "C:\\Users\world\PycharmProjects\Crypto\Binance_BV_coin.json"
    BV_top_file_path = "C:\\Users\world\PycharmProjects\Crypto\BV_TopCoinList.json"
    revenue_type_file_path = "C:\\Users\world\PycharmProjects\Crypto\Binance_BV_revenue.json"
else:
    BV_file_path = "/var/Autobot_seoul/Binance_BV_coin.json"
    BV_top_file_path = "/var/Autobot_seoul/BV_TopCoinList.json"
    revenue_type_file_path = "/var/autobot/Binance_BV_revenue.json"



BV_coinlist = list()
try:
    #이 부분이 파일을 읽어서 리스트에 넣어주는 로직입니다. 
    with open(BV_file_path, 'r') as json_file:
        BV_coinlist = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("BV_coinlist Exception by First")



TopCoinList = list()
#파일을 읽어서 리스트를 만듭니다.
try:
    with open(BV_top_file_path, "r") as json_file:
        TopCoinList = json.load(json_file)

except Exception as e:
    TopCoinList = myBinance.GetTopCoinList(binanceX,20)
    print("TopCoinList Exception by First")



BV_revenue_dict = dict()
try:
    #이 부분이 파일을 읽어서 딕셔너리에 넣어주는 로직입니다. 
    with open(revenue_type_file_path, 'r') as json_file:
        BV_revenue_dict = json.load(json_file)

except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("BV_revenue_dict Exception by First")


##############################################################
#수익율 0.5%를 트레일링 스탑 기준으로 잡는다. 즉 고점 대비 0.5% 하락하면 매도 처리 한다!
#이 수치는 코인에 따라 한 틱만 움직여도 손절 처리 될 수 있으니 
#1.0 이나 1.5 등 다양하게 변경해서 테스트 해보세요!
stop_revenue = 1
##############################################################




#한국시간 9시 -> 0
hour_crit = 20
min_crit = 25
print(hour, minute)

#베스트봇 과정 진행하면서 탑코인 리스트 만들때 아래 같은 경로에 저장하게 만들었기에
#일단 그대로 사용합니다. https://blog.naver.com/zacra/222670663136
#아래의 경로로 저장하게 되면 실제로는 /home/ec2-user/UpbitTopCoinList.json 이 경로에 파일이 저장되게 됩니다.


#거래대금 탑 코인 리스트를 1위부터 내려가며 매수 대상을 찾는다.
#전체 원화 마켓의 코인이 아니라 탑 순위 TopCoinList 안에 있는 코인만 체크해서 매수한다는 걸 알아두세요!
for ticker in TopCoinList:
    try: 
        print("Coin Ticker: ",ticker)
        Target_Coin_Symbol = ticker.replace("/", "")
        #변동성 돌파리스트에 없다. 즉 아직 변동성 돌파 전략에 의해 매수되지 않았다.
        if myBinance.CheckCoinInList(BV_coinlist,ticker) == False:
            
            time.sleep(0.05)
            df = myBinance.GetOhlcv(binanceX,ticker, '1h') #일봉 데이타를 가져온다.
            
            #어제의 고가와 저가의 변동폭에 0.5를 곱해서
            #오늘의 시가와 더해주면 목표 가격이 나온다!
            up_target = float(df['open'][-(hour+1)]) + (float(max(df['high'][-(hour+25):-(hour+1)])) - float(min(df['low'][-(hour+25):-(hour+1)]))) * k_parameter
            down_target = float(df['open'][-(hour+1)]) - (float(max(df['high'][-(hour+25):-(hour+1)])) - float(min(df['low'][-(hour+25):-(hour+1)]))) * k_parameter
            
            #현재가
            now_price = float(df['close'][-1])

            print("현재가 : ",now_price , "상승 타겟 : ", up_target, "하락 타겟 : ", down_target)

            #이를 돌파했다면 변동성 돌파 성공!! 코인을 매수하고 지정가 익절을 걸고 파일에 해당 코인을 저장한다!
            if now_price > up_target and len(BV_coinlist) < MaxCoinCnt: #and myUpbit.GetHasCoinCnt(balances) < MaxCoinCnt:


                for posi in balance_binance['info']['positions']:
                    if posi['symbol'] == Target_Coin_Symbol:
                        back_2_ticker = False

                        #사는 구간
                        if float(posi['positionAmt']) ==0:
                            leverage = float(posi['leverage'])
                            isolated = posi['isolated']
                            break
                        else:
                            #다음 ticker로 넘어가는 구간
                            back_2_ticker = True
                            break

                if back_2_ticker ==True:
                    continue

                print("!!!!!!!!!!!!!!!BV go up!!!!!!!!!!!!!!!!!!!!!!!!")

                #노이즈 계산 구간
                noise_range_max = float(max(df['high'][-24:]))
                noise_range_min = float(min(df['low'][-24:]))
                noise_range_open = float(df['open'][-24])
                noise_now = 1-abs((now_price-noise_range_open)/(noise_range_max-noise_range_min))


                minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker)
                Buy_Amt = float(binanceX.amount_to_precision(ticker, season_weight*(average_noise/noise_now)*(GetInMoney / now_price) * set_leverage))
                Buy_Amt_limit = float(binanceX.amount_to_precision(ticker, (GetInMoney / now_price) * set_leverage))

                if Buy_Amt>=Buy_Amt_limit:
                    Buy_Amt = Buy_Amt_limit
                # 최소 주문 수량보다 작다면 이렇게 셋팅!
                if Buy_Amt < minimun_amount:
                    Buy_Amt = minimun_amount

                #################################################################################################################
                # 레버리지 셋팅
                if leverage != set_leverage:

                    try:
                        print(binanceX.fapiPrivate_post_leverage(
                            {'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                    except Exception as e:
                        print("Exception:", e)

                #################################################################################################################

                #################################################################################################################
                # 격리 모드로 설정
                if isolated == False:
                    try:
                        print(binanceX.fapiPrivate_post_margintype(
                            {'symbol': Target_Coin_Symbol, 'marginType': 'ISOLATED'}))
                    except Exception as e:
                        print("Exception:", e)
                #################################################################################################################



                #시장가 매수를 한다.

                params = {'positionSide': 'LONG'}
                print(binanceX.create_order(ticker, 'market', 'buy', Buy_Amt, None, params))

                #매수된 코인을 BV_coinlist 리스트에 넣고 이를 파일로 저장해둔다!
                BV_coinlist.append(ticker)

                #파일에 리스트를 저장합니다
                with open(BV_file_path, 'w') as outfile:
                    json.dump(BV_coinlist, outfile)

                ##############################################################
                #매수와 동시에 초기 수익율을 넣는다. (당연히 0일테니 0을 넣고)
                BV_revenue_dict[ticker] = 0

                #파일에 딕셔너리를 저장합니다
                with open(revenue_type_file_path, 'w') as outfile:
                    json.dump(BV_revenue_dict, outfile)
                ##############################################################

                #이렇게 매수했다고 메세지를 보낼수도 있다
                line_alert.SendMessage_SP("Start DolPa Coin : " + ticker)

            elif now_price < down_target and len(BV_coinlist) < MaxCoinCnt:
                for posi in balance_binance['info']['positions']:
                    if posi['symbol'] == Target_Coin_Symbol:
                        back_2_ticker = False

                        # 사는 구간
                        if float(posi['positionAmt']) == 0:
                            leverage = float(posi['leverage'])
                            isolated = posi['isolated']
                            break

                        # 이미 포지션 잡고 있는 코인이기 때문에, 다음 티커로 넘어가는 코드
                        else:
                            # 다음 ticker로 넘어가는 구간
                            back_2_ticker = True
                            break

                if back_2_ticker == True:
                    continue
                print("!!!!!!!!!!!!!!!BV go down!!!!!!!!!!!!!!!!!!!!!!!!")

                # 노이즈 계산 구간
                noise_range_max = float(max(df['high'][-24:]))
                noise_range_min = float(min(df['low'][-24:]))
                noise_range_open = float(df['open'][-24])
                noise_now = 1 - abs((now_price - noise_range_open) / (noise_range_max - noise_range_min))

                minimun_amount = myBinance.GetMinimumAmount(binanceX, ticker)
                Buy_Amt = float(binanceX.amount_to_precision(ticker, season_weight*(average_noise/noise_now)*(GetInMoney / now_price) * set_leverage))

                Buy_Amt_limit = float(binanceX.amount_to_precision(ticker, (GetInMoney / now_price) * set_leverage))

                if Buy_Amt >= Buy_Amt_limit:
                    Buy_Amt = Buy_Amt_limit

                if Buy_Amt < minimun_amount:
                    Buy_Amt = minimun_amount

                    try:
                        print(binanceX.fapiPrivate_post_leverage({'symbol': Target_Coin_Symbol, 'leverage': set_leverage}))
                    except Exception as e:
                        print("Exception:", e)

                params = {'positionSide': 'SHORT'}
                print(binanceX.create_order(ticker, 'market', 'sell', Buy_Amt, None, params))

                # 매수된 코인을 BV_coinlist 리스트에 넣고 이를 파일로 저장해둔다!
                BV_coinlist.append(ticker)

                # 파일에 리스트를 저장합니다
                with open(BV_file_path, 'w') as outfile:
                    json.dump(BV_coinlist, outfile)

                ##############################################################
                # 매수와 동시에 초기 수익율을 넣는다. (당연히 0일테니 0을 넣고)
                BV_revenue_dict[ticker] = 0

                # 파일에 딕셔너리를 저장합니다
                with open(revenue_type_file_path, 'w') as outfile:
                    json.dump(BV_revenue_dict, outfile)
                ##############################################################

                # 이렇게 매수했다고 메세지를 보낼수도 있다
                line_alert.SendMessage_SP("Start DolPa Coin : " + ticker)

        else:
            print("기준시간에 모두 매도하게 코드 짜줘")




    except Exception as e:
        print("---:", e)





#모든 원화마켓의 코인을 순회하여 체크한다!
# 이렇게 두번에 걸쳐서 for문을 도는 이유는
# 매수된 코인이 거래대금 탑순위에 (TopCoinList) 빠져서 아예 체크되지 않은 걸 방지하고자
# 매수 후 체크하는 로직은 전체 코인 대상으로 체크하고
# 매수 할때는 TopCoinList안의 코인만 체크해서 매수 합니다.


Tickers = pyupbit.get_tickers("KRW")

for ticker in Tickers:
    try: 
        print("Coin Ticker: ",ticker)

        #변동성 돌파로 매수된 코인이다!!! (실제로 매도가 되서 잔고가 없어도 파일에 쓰여있다면 참이니깐 이 안의 로직을 타게 됨)
        if myUpbit.CheckCoinInList(BV_coinlist,ticker) == True:


            #아침 9시 0분에 체크해서 보유 중이라면 (아직 익절이나 손절이 안된 경우) 매도하고 리스트에서 빼준다!
            if hour == 0 and min == 0:

                #매수한 코인이라면.
                if myUpbit.IsHasCoin(balances, ticker) == True:
                    #시장가로 모두 매도!
                    balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))

                #리스트에서 코인을 빼 버린다.
                BV_coinlist.remove(ticker)

                #파일에 리스트를 저장합니다
                with open(dolpha_type_file_path, 'w') as outfile:
                    json.dump(BV_coinlist, outfile)
            


            #영상에 빠져 있지만 이렇게 매수된 상태의 코인인지 체크하고 난뒤 진행합니다~!
            if myUpbit.IsHasCoin(balances, ticker) == True:

                #수익율을 구한다.
                revenue_rate = myUpbit.GetRevenueRate(balances,ticker)

                ##############################################################
                #방금 구한 수익율이 파일에 저장된 수익율보다 높다면 갱신시켜준다!
                if revenue_rate > BV_revenue_dict[ticker]:

                    #이렇게 딕셔너리에 값을 넣어주면 된다.
                    BV_revenue_dict[ticker] = revenue_rate
                    
                    #파일에 딕셔너리를 저장합니다
                    with open(revenue_type_file_path, 'w') as outfile:
                        json.dump(BV_revenue_dict, outfile)

                #그게 아닌데 
                else:
                    #고점 수익율 - 스탑 수익율 >= 현재 수익율... 즉 고점 대비 0.5% 떨어진 상황이라면 트레일링 스탑!!! 모두 매도한다!
                    if (BV_revenue_dict[ticker] - stop_revenue) >= revenue_rate:
                        #시장가로 모두 매도!
                        balances = myUpbit.SellCoinMarket(upbit,ticker,upbit.get_balance(ticker))

                        #이렇게 손절했다고 메세지를 보낼수도 있다
                        line_alert.SendMessage("Finish DolPa Coin : " + ticker + " Revenue rate:" + str(revenue_rate))

                ##############################################################





    except Exception as e:
        print("---:", e)
