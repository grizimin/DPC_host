import asyncio
import secrets

from websockets.asyncio.server import serve

sessions = {}


def generate_session_id():
    while True:
        session_id = secrets.token_hex(3).upper()

        if session_id not in sessions:
            return session_id


async def handler(ws):
    role = None
    session_id = None

    try:
        async for message in ws:
            message = message.strip()

            # Desktop creates session
            if message == "CREATE":
                if role is not None:
                    continue

                session_id = generate_session_id()
                role = "desktop"

                sessions[session_id] = {
                    "desktop": ws,
                    "mobiles": set(),
                }

                await ws.send(f"SESSION {session_id}")
                print(f"Desktop created session {session_id}")

            # Mobile joins session
            elif message.startswith("JOIN "):
                if role is not None:
                    continue

                requested_session = message[5:].strip()

                if requested_session not in sessions:
                    await ws.send("ERROR")
                    continue

                session = sessions[requested_session]

                session["mobiles"].add(ws)

                role = "mobile"
                session_id = requested_session

                await ws.send("OK")

                print(f"Mobile joined {session_id}")

            # Forward input from mobile to desktop
            else:
                if role != "mobile":
                    continue

                session = sessions.get(session_id)

                if session is None:
                    continue

                desktop = session["desktop"]

                try:
                    await desktop.send(message)
                except Exception:
                    pass

    except Exception as e:
        print("Connection error:", e)

    finally:
        if session_id and session_id in sessions:
            session = sessions[session_id]

            if role == "desktop":
                print(f"Closing session {session_id}")

                for mobile in list(session["mobiles"]):
                    try:
                        await mobile.close()
                    except Exception:
                        pass

                del sessions[session_id]

            elif role == "mobile":
                session["mobiles"].discard(ws)


async def main():
    async with serve(handler, "0.0.0.0", 8766):
        print("Server started on :8766")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
