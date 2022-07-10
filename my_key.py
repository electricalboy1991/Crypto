#-*-coding:utf-8 -*-

'''
여러분의 시크릿 키와 엑세스 키를 
ende_key.py에 있는 키를 활용해서 암호화한 값을 넣으세요

마찬가지 방법으로 아래 로직을 실행하시면 됩니다.. (ende_key.py 참조)

from cryptography.fernet import Fernet

class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou

         

simpleEnDecrypt = SimpleEnDecrypt(b'NcUgge50agCYGXpJmpcxsE5_0do84kKNdI6DsG-iwm8=') #ende_key.py 에 있는 키를 넣으세요

access = "A0X27AGgl8UYAC2cFMYzyrMlfxn1DsgrxoGjLVc2"          # 본인 값으로 변경
secret = "JkaADmlhsKOAcOlSsYw1WJ7DIpSnM9gGzP7dLRBx"          # 본인 값으로 변경


print("access_key: ", simpleEnDecrypt.encrypt(access))

print("scret_key: ", simpleEnDecrypt.encrypt(secret))

'''

upbit_access = "gAAAAABiwBpCWB_ArMZqjeCApgue6YfSO4lgxg32gN4UsqiKnls-q0RN20Smqhf8Dp0a0Aszad1uGWkpFWMtymec6Kzql8TtULvRkZ_mXZxTBUpiccwMU7RfvvRaY8ExYgH9GaO8wg6G"          # 본인 값으로 변경
upbit_secret = "gAAAAABiwBpCmbivavaNxdKXGQmFjlW4DbxU0yufsAtzFOPCzbCQbDBpr_V5oUhwcL_iNE3JqFjlX4PndK7Z9RnPg6aeEoLcsJ-b_dSWAl6Y1R9isbV2P2l0Y107v_i2fvScOMMPo-tW"

binance_access =  "gAAAAABiwzuSPey4dRm1SOQvIwSGD9lICuBkemdT8HMni_Nw3BrTAFTC4pxhboN2g5_rVFDhb94p-wgGOHyjkgSj81Ah0XXbteYG3rwKHLhE0Va5fIxQjFcXkuU0Wgdb9zPzP1U5rHhJDh0UyeHgTfcdTa-UldpekCnSbIOeXcKg9erHxKufFx4="
binance_secret =  "gAAAAABiwzuSIyolbijloyqTJspUg1We7pnePwjo9MuybvDirAOFL3yZiBnpXvYkGfueowGBMueXSFOC1l-STwIDVHfaqxGo5X1JQh5NFvnIwt4sVMmOToN39-QmaurzkiSAMfAKua3C4f0L8VHceF8YYY_P_y7OPMaoMfSiZ4_6aluu2p0D7PU="
