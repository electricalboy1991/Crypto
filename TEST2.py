import http.client

conn = http.client.HTTPSConnection(“data.fixer.io”)
payload = ”
headers = {}
conn.request(“GET”, “/api/latest?access_key=c0*****f”, payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode(“utf-8”))