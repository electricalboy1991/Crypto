import asyncio
import json
import websockets

async def subscribe(symbols):
    uri = "wss://fstream.binance.com/stream?streams="
    for symbol in symbols:
        uri += symbol.lower() + "@ticker/" + symbol.lower() + "@depth20" + "/"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            print(json.loads(response))

symbols = ["BTCBUSD", "ETHBUSD", "XRPBUSD", "DOGEUSDT"]
asyncio.get_event_loop().run_until_complete(subscribe(symbols))