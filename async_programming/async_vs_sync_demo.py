"""
FastAPI demos: sync vs async, concurrency with await, and wrapping blocking work.

Run:
  uvicorn async_programming.async_vs_sync_demo:app --reload

References:
- FastAPI Concurrency and async/await: https://fastapi.tiangolo.com/async/
"""

import time
import asyncio
from typing import Dict, List
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool


app = FastAPI(title="Async vs Sync Demo")


# --- Helpers ---------------------------------------------------------------

def blocking_io_task(duration_seconds: float) -> str:
    # Simulates blocking I/O (e.g., requests, database driver without async)
    time.sleep(duration_seconds)
    return f"blocking_io_task({duration_seconds}s) done"


async def async_io_task(duration_seconds: float) -> str:
    # Simulates non-blocking async I/O
    await asyncio.sleep(duration_seconds)
    return f"async_io_task({duration_seconds}s) done"


# --- 1) Pure sync endpoint (def) ------------------------------------------

@app.get("/sync/noawait")
def sync_noawait() -> Dict[str, str]:
    # Uses blocking code directly. In FastAPI, this runs in a threadpool.
    result = blocking_io_task(1.5)
    return {"mode": "sync", "detail": result}


# --- 2) Pure async endpoint (async def) -----------------------------------

@app.get("/async/await-one")
async def async_await_one() -> Dict[str, str]:
    # Uses non-blocking await; event loop stays free to serve other requests.
    result = await async_io_task(1.5)
    return {"mode": "async", "detail": result}


# --- 3) Async concurrency: run tasks concurrently with gather -------------

@app.get("/async/await-many")
async def async_await_many() -> Dict[str, List[str]]:
    # Three async tasks run concurrently; total ~ max(duration)
    tasks = [async_io_task(1.0), async_io_task(1.5), async_io_task(0.5)]
    results = await asyncio.gather(*tasks)
    return {"mode": "async_concurrent", "details": results}


# --- 4) Mixing: wrap blocking sync work so it doesn't block event loop ----

@app.get("/async/wrap-blocking")
async def async_wrap_blocking() -> Dict[str, str]:
    # Offload blocking function to threadpool to avoid blocking the event loop
    result = await run_in_threadpool(blocking_io_task, 1.5)
    return {"mode": "async_wrapped_blocking", "detail": result}


# --- 5) Contrast: calling blocking code directly inside async (anti-pattern)

@app.get("/async/bad-blocking")
async def async_bad_blocking() -> Dict[str, str]:
    # WARNING: This blocks the event loop; other requests wait.
    # Shown here only to illustrate the difference.
    time.sleep(1.5)
    return {"mode": "async_bad", "detail": "blocked event loop for 1.5s"}


# --- 6) CPU-bound simulation: consider process pool (not shown) -----------

def cpu_bound_task(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


@app.get("/async/cpu-bound")
async def async_cpu_bound() -> Dict[str, int]:
    # For quick demo, run CPU work in threadpool to keep loop responsive.
    # For heavy CPU, prefer a process pool (e.g., anyio.to_process.run_sync).
    result = await run_in_threadpool(cpu_bound_task, 1_000_00)
    return {"sum_sq": result}


# --- 7) Simple index with guidance ---------------------------------------

@app.get("/")
def index() -> Dict[str, str]:
    return {
        "sync": "/sync/noawait",
        "async_one": "/async/await-one",
        "async_many": "/async/await-many",
        "wrap_blocking": "/async/wrap-blocking",
        "bad_blocking": "/async/bad-blocking",
        "cpu_bound": "/async/cpu-bound",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


