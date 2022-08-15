
Krate_average = 1

if Krate_average <= 0:
    profit_rate = 2.6
elif 0 < Krate_average <= 1:
    profit_rate = 2.1
elif 1 < Krate_average <= 2:
    profit_rate = 1.6
elif 2 < Krate_average <= 2.5:
    profit_rate = 1.2
else:
    profit_rate = 1.0


print(profit_rate)