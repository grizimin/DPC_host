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
options = "p:s"
long_options = ["port=", "silent"]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
port = 8765
silentMode = False 

try:
    arguments, values = getopt.getopt(args, options, long_options)
    for currentArg, currentVal in arguments:
        if currentArg in ("-p", "--port"):
            port = currentVal
        if currentArg in ("-s", "--silent"):
            silentMode = True
except getopt.error as err:
    print(str(err))

def signal_handler(signal, frame):
    print('\nServer is stopped')
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
        log("Press Ctrl+C to stop the server")
        await asyncio.Future()  
                

if __name__ == "__main__":
    asyncio.run(main())
