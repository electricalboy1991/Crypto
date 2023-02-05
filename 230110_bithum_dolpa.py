import pybithumb

def Dolta_go_up(ticker, k):
    df = pybithumb.get_ohlcv(ticker)

    range = (df['high'] - df['low']) * k
    target_long = df['open'] + range.shift(1)

    criteria = df['high'] >= target_long
    buy = target_long[criteria]
    sell = df.loc[criteria, 'close']

    profit_rate = sell / buy
    return profit_rate.cumprod().iloc[-1]

def Dolta_go_down(ticker, k):
    df = pybithumb.get_ohlcv(ticker)

    range = (df['high'] - df['low']) * k
    target_short = df['open'] - range.shift(1)

    criteria = df['high'] >= target_short
    short = target_short[criteria]
    long = df.loc[criteria, 'close']

    profit_rate = (short-long) / short
    return profit_rate.cumprod().iloc[-1]


