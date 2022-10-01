import requests
from bs4 import BeautifulSoup as bs

page = requests.get("https://coinmarketcap.com/ko/currencies/tether/")
soup = bs(page.text, "html.parser")

elements2 = soup.select_one('div.priceValue span').get_text()

TetherKRW=float(elements2[1]+elements2[3:9])

