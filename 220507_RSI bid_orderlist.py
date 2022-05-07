import pyupbit
access_key = "mpCGRiTCqlza4eKywK6AIikXQ9ABX3dqQkyuTc3w"
secret_key = "megYxQfiLpuII681da1vlX2bC9EcGXI0iyg6odSQ"
server_url = "https://api.upbit.com"

upbit = pyupbit.Upbit(access_key, secret_key)
print(upbit.get_balance(ticker="KRW"))