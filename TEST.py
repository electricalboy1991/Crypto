import requests

def get_usd_krw():
    url = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
    params = {
        "authkey": "I4fUIUhXyIfSChg5Q2OWBel4i3aJnfXy",
        "searchdate": "2023-04-20",
        "data": "AP01"
    }
    response = requests.get(url, params=params)
    data = response.json()
    for item in data:
        if item["cur_unit"] == "USD":
            return float(item["ttb"].replace(",", ""))
    return None

print(get_usd_krw())