import asyncio
import json
import websockets


SESSION_ID = "9F7FCA"


async def main():
    async with websockets.connect("ws://localhost:8765") as ws:
        await ws.send(json.dumps({
            "type": "join_session",
            "session_id": SESSION_ID,
        }))

        print(await ws.recv())

        while True:
            text = input("> ")

            #for ch in text:
            #    await ws.send(json.dumps({
            #        "type": "input",
            #        "text": ch,
            #    }))
            await ws.send(json.dumps({
                "type": "input",
                "text": text
            }))


asyncio.run(main())