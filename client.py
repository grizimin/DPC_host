import asyncio
import websockets

async def test():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello server!")
        reply = await websocket.recv()
        print(reply)

asyncio.run(test())
