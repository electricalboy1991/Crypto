import numpy as np
import matplotlib.pyplot as plt

# 설정값
initial_stock_price = 10.0  # 초기 주식 가격: $10
daily_return = 0.01  # 주식의 일일 변동률: 1%
rebalancing_period = 250  # 리벨런싱 주기: 30일
total_days = 365 * 5  # 시뮬레이션 기간: 5년 (365일 * 5)
initial_cash = 50  # 초기 현금: $50
initial_stock = 5  # 초기 주식: $50 (5주)

# 주식 가격 시뮬레이션
stock_prices = [initial_stock_price]
for _ in range(total_days - 1):
    # 이전 가격을 기준으로 ±1% 범위에서 랜덤하게 변동
    change = 1 + np.random.choice([-daily_return, daily_return])
    new_price = stock_prices[-1] * change
    stock_prices.append(new_price)

# 포트폴리오 가치 시뮬레이션
portfolio_value = []
cash = initial_cash
stock = initial_stock

for i in range(total_days):
    # 현재 주식 가치 계산
    current_stock_value = stock * stock_prices[i]

    # 리벨런싱 조건 체크
    if i % rebalancing_period == 0:
        total_value = cash + current_stock_value
        cash = total_value / 2
        stock = cash / stock_prices[i]
        current_stock_value = stock * stock_prices[i]

    portfolio_value.append(cash + current_stock_value)

# 결과 그래프로 시각화 (두 개의 y축 사용)
# 코드 마지막에 주식 가격과 포트폴리오 가치를 표시하기 위한 코드 추가

# 결과 그래프로 시각화 (두 개의 y축 사용)
fig, ax1 = plt.subplots(figsize=(12, 6))

# 왼쪽 y축: 주식 가격
ax1.plot(stock_prices, label='Stock Price', color='blue')
ax1.set_xlabel('Days')
ax1.set_ylabel('Stock Price in $', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# 오른쪽 y축: 포트폴리오 가치
ax2 = ax1.twinx()  # 공유 x축을 가진 새로운 y축 생성
ax2.plot(portfolio_value, label='Portfolio Value', color='orange')
ax2.set_ylabel('Portfolio Value in $', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# 주식 가격 및 포트폴리오 가치의 마지막 값을 그래프에 표시
final_stock_price = stock_prices[-1]
final_portfolio_value = portfolio_value[-1]
ax1.text(total_days, final_stock_price, f"${final_stock_price:.2f}", color='blue', horizontalalignment='right')
ax2.text(total_days, final_portfolio_value, f"${final_portfolio_value:.2f}", color='orange', horizontalalignment='right')

# 제목 및 그리드 설정
plt.title('Shannon’s Demon Simulation over 5 Years')
fig.tight_layout()  # 레이아웃 조정
plt.grid(True)
plt.show()
