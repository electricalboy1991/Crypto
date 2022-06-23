import pyupbit

upbit_access_key = "mpCGRiTCqlza4eKywK6AIikXQ9ABX3dqQkyuTc3w"
upbit_secret_key = "megYxQfiLpuII681da1vlX2bC9EcGXI0iyg6odSQ"

upbit = pyupbit.Upbit(upbit_access_key, upbit_secret_key)


my_balances = upbit.get_balances()
for coin_balance in my_balances:
    print(coin_balance)