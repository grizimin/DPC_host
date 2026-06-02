import asyncio
import websockets


class DesktopClient:
    def __init__(self, uri):
        self.uri = uri
        self.session_id = None

    async def connect(self):
        async with websockets.connect(self.uri) as ws:
            self.ws = ws

            # 1. Create session
            await self.create_session()

            # 2. Listen for mobile inputs
            await self.listen()

    async def create_session(self):
        await self.ws.send("CREATE")

        response = await self.ws.recv()

        if response.startswith("SESSION "):
            self.session_id = response.split(" ", 1)[1]
            print(f"[Desktop] Session created: {self.session_id}")
        else:
            raise Exception(f"Unexpected response: {response}")

    async def listen(self):
        print("[Desktop] Listening for inputs...")

        async for message in self.ws:
            message = message.strip()

            if message == "L":
                self.on_left()

            elif message == "R":
                self.on_right()

            elif message == "1":
                self.on_button1()

            elif message == "2":
                self.on_button2()

            elif message == "3":
                self.on_button3()

            else:
                print(f"[Desktop] Unknown message: {message}")

    # --- actions ---
    def on_left(self):
        print("⬅ Slide Left")

    def on_right(self):
        print("➡ Slide Right")

    def on_button1(self):
        print("Button 1")

    def on_button2(self):
        print("Button 2")

    def on_button3(self):
        print("Button 3")


if __name__ == "__main__":
    uri = "ws://localhost:8765"
    client = DesktopClient(uri)

    asyncio.run(client.connect())