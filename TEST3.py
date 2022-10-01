import re
import urllib
from urllib.request import Request, urlopen

url = 'https://www.sec.gov/Archives/edgar/data/1547063/000119312513465948/0001193125-13-465948.txt'

response = urllib.request.urlopen(url).read()
p = re.findall('<P((.|\s)+?)< /P>', str(response)) #(pattern, string)

   paragraphs = []
   for x in p:
   paragraphs.append(str(x))