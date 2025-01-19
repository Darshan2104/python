import asyncio
from fastapi import FastAPI, BackgroundTasks
from typing import Dict

app = FastAPI()
task_queue = asyncio.Queue()
MAX_WORKERS = 1
semaphore = asyncio.Semaphore(MAX_WORKERS)

# Worker function to process tasks from the queue
def fun_1(v):
    for i in range(500):
        pass
    return "fun_1"

def fun_2(v):
    return "fun_2"


async def worker():
    while True:
        task = await task_queue.get()
        if task is None:
            break
        async with semaphore:
            await execute_task_with_retries(task)
            await asyncio.sleep(1)
#        await task()

async def execute_task_with_retries(task, retries=3):
    for attempt in range(retries):
        try:
            await task()
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt + 1 == retries:
                print(f"Task failed after {retries} attempts.")
                raise
            await asyncio.sleep(1)

# Function to enqueue tasks
async def process_request(data: Dict):
    await task_queue.put(lambda: pipeline(data))

# Your pipeline logic
def pipeline(data: Dict):
    # Simulate a long-running task
    v = "data"
#    print(fun_1(v))
    #await asyncio.sleep(2)
    #await asyncio.to_thread(fun_1,v)
    import time
    time.sleep(2)
#    loop = asyncio.get_running_loop()
#    result = await loop.run_in_executor(None, fun_1, v)
    result = fun_1(v)
    print(result)
#    result = await loop.run_in_executor(None, fun_2, v)
    result = fun_2(v)
    print(result)
    print(f"Processed: {data}")

@app.post("/process")
async def process(data: Dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_request, data)
    return {"status": "accepted"}

# Startup event to initialize worker pool
@app.on_event("startup")
async def startup_event():
    for _ in range(MAX_WORKERS):
        asyncio.create_task(worker())

# Shutdown event to stop workers
@app.on_event("shutdown")
async def shutdown_event():
    for _ in range(MAX_WORKERS):
        await task_queue.put(None)

