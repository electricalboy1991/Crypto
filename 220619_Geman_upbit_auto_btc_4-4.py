import pyupbit
import pandas as pd

upbit_access_key = "mpCGRiTCqlza4eKywK6AIikXQ9ABX3dqQkyuTc3w"
upbit_secret_key = "megYxQfiLpuII681da1vlX2bC9EcGXI0iyg6odSQ"

upbit = pyupbit.Upbit(upbit_access_key, upbit_secret_key) #업비트 객체를 만듭니다.

#RSI지표 수치를 구해준다. 첫번째: 분봉/일봉 정보, 두번째: 기간
def GetRSI(ohlcv,period):
    ohlcv["close"] = ohlcv["close"]
    delta = ohlcv["close"].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
    RS = _gain / _loss
    return pd.Series(100 - (100 / (1 + RS)), name="RSI")



#비트코인의 140분봉(캔들) 정보를 가져온다.  
df = pyupbit.get_ohlcv("KRW-BTC",interval="minute240")

#RSI14지표를 구합니다.
rsi14= float(GetRSI(df,14).iloc[-1])

print("BTC_BOT_WORKING")
print("NOW RSI:", rsi14)

#RSI지표가 30이하라면
if rsi14 <= 30:
    #비트코인을 5천원씩 시장가로 매수합니다!
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!IN")
    print(upbit.buy_market_order("KRW-BTC",5000))

