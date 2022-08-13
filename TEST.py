Krate_total = dict()

ticker_upbit = 'KRW-FLOW'
Krate_total[ticker_upbit] = [None,None,None,None,None]

Krate_list= list(filter(None, Krate_total[ticker_upbit]))
print(sum(Krate_list)/len(Krate_list))

