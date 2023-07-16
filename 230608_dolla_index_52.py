import requests
from bs4 import BeautifulSoup

def get_dollar_index():
    url = 'https://www.investing.com/indices/us-dollar-index'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    value = soup.find('span', {'id': 'last_last'}).text.strip()

    return value

# Usage
dollar_index_value = get_dollar_index()
print("Dollar Index Value:", dollar_index_value)
