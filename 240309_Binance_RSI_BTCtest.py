from binance.client import Client
import myBinance # 만든 코드
import ende_key  # 암복호화키
import my_key  # 업비트 시크릿 액세스키

#암복호화 클래스 객체를 미리 생성한 키를 받아 생성한다.
simpleEnDecrypt = myBinance.SimpleEnDecrypt(ende_key.ende_key)

#암호화된 액세스키와 시크릿키를 읽어 복호화 한다.
Binance_AccessKey = simpleEnDecrypt.decrypt(my_key.binance_access)
Binance_ScretKey = simpleEnDecrypt.decrypt(my_key.binance_secret)


# Binance Client 객체 생성
client = Client(Binance_AccessKey, Binance_ScretKey)

loan_amount = '10'  # 대출할 USDT 양
collateral_coin = 'BTC'  # 담보로 사용할 코인
loan_coin = 'USDT'  # 대출받을 코인

# 마진 대출 요청
try:
    # 대출 가능한 금액 확인
    max_loan = client.get_max_margin_loan(asset=loan_coin, collateralCoin=collateral_coin)
    print("최대 대출 가능 금액:", max_loan)

    # 실제 대출 요청
    response = client.create_margin_loan(asset=loan_coin, amount=loan_amount)
    print("대출 성공:", response)
except Exception as e:
    print("오류 발생:", e)


######

# Transfer BTC from spot wallet to margin wallet
response = client.transfer_spot_to_margin(asset='BTC', amount='0.01')
print(response)

# Get max borrowable amount of USDT against BTC collateral
max_borrowable = client.get_max_margin_loan(asset='USDT', collateralCoin='BTC')
print(max_borrowable)

# Borrow USDT against BTC collateral
response = client.create_margin_loan(asset='USDT', amount='50', collateralCoin='BTC')  # 50 USDT as an example
print(response)

result = client.transfer_margin_to_spot(asset=asset, amount=amount)
print("전송 성공:", result)

