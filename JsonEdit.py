import json
TopCoinList_upbit = ['KRW-FLOW','KRW-ETC','KRW-BTC','KRW-NEAR','KRW-ETH','KRW-WAVES','KRW-XRP']

Krate_total = dict()
try:
    with open('C:\\Users\world\PycharmProjects\Crypto\Krate_total.json', 'r') as f:

        Krate_total = json.load(f)

    print(Krate_total)


except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First")

for ticker_upbit in TopCoinList_upbit:
    Krate_total[ticker_upbit] = [2,2,2,2,2]

with open('C:\\Users\world\PycharmProjects\Crypto\Krate_total.json', 'w') as outfile:
    json.dump(Krate_total, outfile)

