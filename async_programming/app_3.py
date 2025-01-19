"""
Queue with threadpooling
"""
from fastapi import FastAPI, Request, BackgroundTasks
import asyncio
import time
from fastapi.concurrency import run_in_threadpool

app = FastAPI()

queue = asyncio.Queue()

async def process_queue():
    while True:
        item = await queue.get()
        await run_in_threadpool(handle_request, item)
        time.sleep(5)
        queue.task_done()

def handle_request(request_data):
    sync_function1()
    sync_function2()
    sync_function3()
    print(f"Processed: {request_data}")

def sync_function1():
    time.sleep(1)

def sync_function2():
    time.sleep(1)

def sync_function3():
    time.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_queue())

@app.post("/process")
async def enqueue_request(request: Request):
    request_data = await request.json()
    await queue.put(request_data)
    return {"status": "queued", "data": request_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
