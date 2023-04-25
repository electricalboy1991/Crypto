import asyncio
import json
import websockets

async def subscribe_upbit(symbols):
    uri = "wss://api.upbit.com/websocket/v1"

    subscribe_msg = [{"ticket":"UNIQUE_TICKET"}]
    for symbol in symbols:
        subscribe_msg.append({"type":"orderbook", "codes":[f"KRW-{symbol}"], "isOnlyRealtime":True})

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(subscribe_msg))

        while True:
            response = await websocket.recv()
            print(json.loads(response))

async def subscribe_binance(symbols):
    uri = "wss://fstream.binance.com/stream?streams="
    for symbol in symbols:
        uri += symbol.lower() + "@ticker/" + symbol.lower() + "@depth20" + "/"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            print(json.loads(response))

symbols_upbit = ["BTC", "ETH", "XRP", "DOGE"]
symbols_binance = ["BTCBUSD", "ETHBUSD", "XRPBUSD", "DOGEUSDT"]

async def subscribe_all():
    task_upbit = asyncio.create_task(subscribe_upbit(symbols_upbit))
    task_binance = asyncio.create_task(subscribe_binance(symbols_binance))
    await asyncio.gather(task_upbit, task_binance)

asyncio.get_event_loop().run_until_complete(subscribe_all())
