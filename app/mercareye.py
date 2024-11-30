# mercareye.py

import asyncio

import config
import search

async def main():

    # Initialize
    config.load()
    search.load()

    # Start search loop
    await search.start()

if __name__ == "__main__":
    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass