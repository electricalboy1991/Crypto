# 체결했으니까 내역 업데이트 해서 받아오기
                    balance_binanace = binanceX.fetch_balance(params={"type": "future"})
                    upbit = pyupbit.Upbit(Upbit_AccessKey, Upbit_ScretKey)
                    time.sleep(0.1)
                    balance_upbit = upbit.get_balances()

                    for posi in balance_binanace['info']['positions']:
                        if posi['symbol'] == Target_Coin_Symbol and posi['positionSide'] == 'SHORT':
                            print(posi)
                            amt_s = float(posi['positionAmt'])
                            entryPrice_s = float(posi['entryPrice'])
                            leverage = float(posi['leverage'])
                            isolated = posi['isolated']
                            break
                    for upbit_asset in balance_upbit:
                        if upbit_asset['currency'] == 'KRW':
                            upbit_remain_money = float(upbit_asset['balance'])
                        else:
                            continue

                    stop_price_binance = entryPrice_s * (1 + 1 / set_leverage) * Stop_price_percent
                    stop_price_upbit = myUpbit.GetAvgBuyPrice(balance_upbit, ticker_upbit) * (1 + 1 / set_leverage) * Stop_price_percent
                    time.sleep(0.1)
                    myBinance.SetStopLossShortPrice(binanceX, ticker_binance, stop_price_binance, False)

                    myUpbit.CancelCoinOrder(upbit, ticker_upbit)
                    coin_volume = upbit.get_balance(ticker_upbit)
                    myUpbit.SellCoinLimit(upbit, ticker_upbit, stop_price_upbit, coin_volume)

                    ADMoney_index=Situation_flag[ticker_upbit].index(False)


                    Situation_flag[ticker_upbit][ADMoney_index] = True
                    with open(Situation_flag_type_file_path, 'w') as outfile:
                        json.dump(Situation_flag, outfile)

                    Krate_total[ticker_upbit][ADMoney_index] = Krate
                    with open(Krate_total_type_file_path, 'w') as outfile:
                        json.dump(Krate_total, outfile)

                    #물을 탔다는 의미임
                    Trade_infor[ticker_upbit][1] = 1
                    with open(Trade_infor_path, 'w') as outfile:
                        json.dump(Trade_infor, outfile)
                    time.sleep(0.1)

                    line_alert.SendMessage_SP("[청산 경고 물] : " + str(ticker_upbit[4:]) + " " + str(round(Buy_Amt * upbit_order_standard / 10000, 1)) + "만원 " + "김프 : " + str(round(Krate, 2)))
                    line_alert.SendMessage_Trading(str(ticker_upbit)+ " BUSD KRW : " + str(BUSDKRW)+" 시장가 : " + str(now_price_upbit) + str(now_price_binance) + "\n김프 계산 가격 : " + str(upbit_order_standard) + ' ' + str(binance_order_standard)+
                        "\n업빗 호가창 : \n" + str(orderbook_upbit['orderbook_units'][:4]) + "\n바낸 호가창 : \n" + str(binance_orderbook_data))
