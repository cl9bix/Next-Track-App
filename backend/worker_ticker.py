import asyncio
import os

from app.services.event_runtime import ticker_loop, start_event_if_needed

EVENT_ID = int(os.getenv("EVENT_ID", "1"))

async def main():
    await start_event_if_needed(EVENT_ID)
    stop = asyncio.Event()
    await ticker_loop(EVENT_ID, stop_event=stop)

if __name__ == "__main__":
    asyncio.run(main())
