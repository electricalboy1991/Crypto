import numpy as np
import matplotlib.pyplot as plt

# 시뮬레이션 매개변수 설정
initial_stock_price = 10  # 초기 주식 가격
initial_cash = 10         # 초기 현금
total_days = 5 * 252      # 5년 (주식 시장은 연간 약 252일 개장)
rebalance_interval = 30   # 리밸런싱 주기 (30일)
volatility = 0.01         # 주식 가격 변동성 (일일)

# 주식 가격 시뮬레이션
np.random.seed(0)  # 일관된 결과를 위한 난수 생성기 초기화
stock_prices = np.zeros(total_days)
stock_prices[0] = initial_stock_price

for t in range(1, total_days):
    # 주식 가격을 랜덤 워크로 모델링
    stock_prices[t] = stock_prices[t - 1] * np.exp(np.random.normal(0, volatility))

# 자산 시뮬레이션
stock_value = initial_stock_price  # 현재 주식 가치
cash = initial_cash                # 현재 현금
total_assets = []                 # 총 자산 기록

for t in range(total_days):
    # 주식 가치 갱신
    stock_value = stock_prices[t] * (stock_value / stock_prices[t - 1])

    # 리밸런싱
    if t % rebalance_interval == 0 and t > 0:
        total = stock_value + cash
        stock_value = total / 2
        cash = total / 2

    # 총 자산 기록
    total_assets.append(stock_value + cash)
plt.figure(figsize=(10, 6))

# 총 자산 가치
plt.plot(total_assets, label='Total Assets', color='blue')
plt.ylabel('Total Asset Value', color='blue')
plt.xlabel('Days')
plt.title('Asset Value and Stock Price Over Time with Final Values')
plt.legend(loc='upper left')
plt.grid(True)

# 주식 가격 변화 (추가 축 사용)
ax2 = plt.gca().twinx()
ax2.plot(stock_prices, label='Stock Price', color='green')
ax2.set_ylabel('Stock Price', color='green')
ax2.legend(loc='upper right')

# 마지막 값 표시
final_stock_price = stock_prices[-1]
final_portfolio_value = total_assets[-1]
plt.text(total_days, final_portfolio_value, f'${final_portfolio_value:.2f}', color='blue', horizontalalignment='right')
ax2.text(total_days, final_stock_price, f'${final_stock_price:.2f}', color='green', horizontalalignment='right')

plt.show()