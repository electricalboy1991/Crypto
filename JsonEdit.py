import json


try:
    with open('C:\\Users\world\PycharmProjects\Crypto\Situation_flag.json', 'r') as f:

        Situation_flag = json.load(f)

    print(Situation_flag)


except Exception as e:
    #처음에는 파일이 존재하지 않을테니깐 당연히 예외처리가 됩니다!
    print("Exception by First")

Situation_flag['KRW-ETH'] = 1
with open('C:\\Users\world\PycharmProjects\Crypto\Situation_flag.json', 'w') as outfile:
    json.dump(Situation_flag, outfile)

