import pybithumb

def get_target_price():
    df = pybithumb.get_ohlcv("BTC")
    volatility = (df.iloc[-2]['high'] - df.iloc[-2]['low']) * 0.6
    target_price = df.iloc[-1]['open'] + volatility
    return target_price

target_price = get_target_price()
print(target_price)