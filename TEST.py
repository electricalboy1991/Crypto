PNL = 0
            isolated_cost = 0
            for posi in balance_binance['info']['positions']:
                if posi['symbol'] == Target_Coin_Symbol and float(posi['positionAmt']) != 0:
                    # 사는 구간
                    entryPrice = float(posi['entryPrice'])
                    PNL = float(posi['unrealizedProfit'])
                    isolated_cost = float(posi['isolatedWallet'])