import asyncio
import json
import websockets

async def subscribe(symbol):
    uri = "wss://fstream.binance.com/ws/" + symbol.lower() + "@ticker/" + symbol.lower() + "@depth"
    async with websockets.connect(uri) as websocket:
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": [
                symbol.lower() + "@ticker",
                symbol.lower() + "@depth20" # subscribe to 10 levels of order book updates
            ],
            "id": 1
        }
        await websocket.send(json.dumps(subscribe_msg))

        while True:
            response = await websocket.recv()
            print(json.loads(response))

symbol = "BTCBUSD"
asyncio.get_event_loop().run_until_complete(subscribe(symbol))