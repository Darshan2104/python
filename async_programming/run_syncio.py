import asyncio

def sync_function():
    # Your synchronous logic
    pass

async def main():

#    result = await asyncio.to_thread(sync_function)  # Python 3.9+
    # or for older versions:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, sync_function)

asyncio.run(main())
