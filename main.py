import asyncio
import websockets
import keyboard
import socket
import subprocess
import signal
import sys
import getopt
from pathlib import Path 

args = sys.argv[1:]
options = "p:sw:gl:"
long_options = ["port=", "silent", "word=", "global"]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
port = 8765
silentMode = False 
globalMode = False
password = ""

try:
    arguments, values = getopt.getopt(args, options, long_options)
    for currentArg, currentVal in arguments:
        if currentArg in ("-p", "--port"):
            port = currentVal
        if currentArg in ("-w", "--word"):
            password = currentVal
        if currentArg in ("-s", "--silent"):
            silentMode = True
        if currentArg in ("-g", "--global"):
            globalMode = True
except getopt.error as err:
    print(str(err))

def signal_handler(signal, frame):
    print('\nServer is stopped')
    asyncio.Future().done()
    sys.exit(0)
 
signal.signal(signal.SIGINT, signal_handler)

def log(string):
    if not silentMode:
        print(string)

def functionButton(id):
    if (Path(f"script{id}.sh").exists()):
        subprocess.run(f"./script{id}.sh")    
    else:
        log(f"File script{id}.sh does not exit")

async def handler(websocket):
    log("Client connected")

    try:
        auth_message = await websocket.recv()

        if not auth_message.startswith("AUTH "):
            await websocket.send("ERROR Unauthorized")
            await websocket.close()
            return
        
        auth_password = auth_message[5:]

        if auth_password != password:
            log("Incorrect password")
            await websocket.send("ERROR Incorrect password")
            await websocket.close()
            return

        await websocket.send("OK")
        log("Auth Completed")

        async for message in websocket:
            if message == "L":
                keyboard.send("left")  
                log("Button Left was pressed")
            elif message == "R":
                keyboard.send("right")
                log("Button Right was pressed")
            elif message == "1" or message == "2" or message == "3":
                id = int(message)
                functionButton(id)
                log(f"Button {id} was pressed")
            else:
                log(f"Unknown message recieved: {message}")
                
    except websockets.ConnectionClosed:
        log("Client disconnected")

async def main():
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"DPC server is now served on {ip}:{port}")
        if password == "":
            print("No password is used")
        else:
            print("Auth with password \"", password, '"', sep="")
        log("Press Ctrl+C to stop the server")
        await asyncio.Future()  

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
                keyboard.send("left")
                log("Button Left was pressed")

            elif message == "R":
                keyboard.send("right")
                log("Button Right was pressed")

            elif message == "1" or message == "2" or message == "3":
                id = int(message)
                functionButton(id)
                log(f"Button {id} was pressed")
            else:
                print(f"[Desktop] Unknown message: {message}")

if __name__ == "__main__":
    if not globalMode:
        asyncio.run(main())
    else:
        uri = "ws://localhost:8765"
        client = DesktopClient(uri)

        asyncio.run(client.connect())
