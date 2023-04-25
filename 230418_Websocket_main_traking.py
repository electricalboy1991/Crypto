import asyncio
import json
import websockets

global binance_order_books, upbit_order_books
binance_order_books = {}
upbit_order_books = {}


async def subscribe_upbit(symbols):
    uri = "wss://api.upbit.com/websocket/v1"

    subscribe_msg = [{"ticket": "UNIQUE_TICKET"}]
    for symbol in symbols:
        subscribe_msg.append({"type": "orderbook", "codes": [f"KRW-{symbol}"], "isOnlyRealtime": True})

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(subscribe_msg))

        while True:
            response = await websocket.recv()
            data = json.loads(response)

            symbol = data['code'].split('-')[1]
            bids = data['orderbook_units'][:20]
            asks = data['orderbook_units'][-20:]
            upbit_order_books[symbol] = {'bids': bids, 'asks': asks}
            print(len(upbit_order_books))
async def subscribe_binance(symbols):
    uri = "wss://fstream.binance.com/stream?streams="
    for symbol in symbols:
        uri += symbol.lower() + "@depth20" + "/"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            # print(data)
            symbol = data['stream'].split('@')[0].upper()
            bids = data['data']['b'][:20]
            asks = data['data']['a'][:20]
            binance_order_books[symbol] = {'bids': bids, 'asks': asks}

async def perform_arbitrage(symbols):
    global binance_order_books, upbit_order_books

    while True:
        print(len(binance_order_books))
        for symbol in symbols:
            if symbol in binance_order_books and symbol in upbit_order_books:
                binance_bids = binance_order_books[symbol]['bids']
                binance_asks = binance_order_books[symbol]['asks']
                upbit_bids = upbit_order_books[symbol]['bids']
                upbit_asks = upbit_order_books[symbol]['asks']

                # Perform arbitrage analysis here
                # ...
                # ...

        await asyncio.sleep(0.1)


symbols_upbit = ["BTC", "ETH", "XRP", "DOGE"]
symbols_binance = ["BTCBUSD", "ETHBUSD", "XRPBUSD", "DOGEBUSD"]


async def subscribe_all():
    task_upbit = asyncio.create_task(subscribe_upbit(symbols_upbit))
    task_binance = asyncio.create_task(subscribe_binance(symbols_binance))
    task_arbitrage = asyncio.create_task(perform_arbitrage(symbols_upbit))
    await asyncio.gather(task_upbit, task_binance, task_arbitrage)


asyncio.get_event_loop().run_until_complete(subscribe_all())
