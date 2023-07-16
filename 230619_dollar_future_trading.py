import yfinance as yf

def get_exchange_rate():
    ticker = yf.Ticker("USDKRW=X")  # Yahoo Finance symbol for USD to PHP exchange rate
    exchange_rate = ticker.history().tail(1)["Close"].values[0]
    return exchange_rate

usd_to_krw = get_exchange_rate()
print("Current exchange rate (USD to KRW):", usd_to_krw)
