import asyncio
import json
import websockets

async def subscribe(symbols):
    uri = "wss://api.upbit.com/websocket/v1"

    subscribe_msg = [{"ticket":"UNIQUE_TICKET"}]
    for symbol in symbols:
        subscribe_msg.append({"type":"orderbook", "codes":[f"KRW-{symbol}"], "isOnlyRealtime":True})

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(subscribe_msg))

        while True:
            response = await websocket.recv()
            print(json.loads(response))

# symbols = ["BTC", "ETH", "XRP", "DOGE"]
symbols = "BTC"
asyncio.get_event_loop().run_until_complete(subscribe(symbols))