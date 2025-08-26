# Async, Sync, Threading, and Concurrency in FastAPI

This guide explains the differences between synchronous code, asynchronous code, multithreading, and multiprocessing in the context of FastAPI. It pairs with `async_vs_sync_demo.py` containing runnable examples.

Reference: FastAPI docs on concurrency and async/await: [fastapi.tiangolo.com/async](https://fastapi.tiangolo.com/async/)

## TL;DR
- Use `async def` when calling libraries you must `await` (non-blocking I/O).
- Use `def` for blocking libraries (e.g., drivers without async). FastAPI runs them in a threadpool.
- For CPU-bound work, prefer processes; threads can help responsiveness but are limited by the GIL.
- Never call `time.sleep()` inside `async def` — use `await asyncio.sleep()` instead.

## Mental Model
- **Synchronous (blocking)**: The current thread waits until the operation completes. Examples: `time.sleep()`, blocking DB/HTTP clients.
- **Asynchronous (non-blocking)**: The function yields control with `await`, letting the event loop serve other requests while waiting.
- **Multithreading**: Multiple OS threads can run blocking tasks so the event loop stays responsive.
- **Multiprocessing**: Multiple processes for CPU-bound work to utilize multiple cores and bypass the GIL.

## Project Files
- `async_vs_sync_demo.py`: Endpoints showcasing sync vs async, concurrency, and safe wrapping of blocking code.

## How to Run
```bash
uvicorn async_programming.async_vs_sync_demo:app --reload
```

## Endpoints Summary
- `/sync/noawait`: Sync endpoint using blocking I/O. FastAPI runs it in a threadpool.
- `/async/await-one`: Pure async approach with `await asyncio.sleep` (non-blocking).
- `/async/await-many`: Concurrent `await` with `asyncio.gather` (runs concurrently; total time ~ max(duration)).
- `/async/wrap-blocking`: Wrap blocking work using a threadpool (`run_in_threadpool`).
- `/async/bad-blocking`: Anti-pattern: `time.sleep()` inside `async def` blocks the event loop.
- `/async/cpu-bound`: CPU task offloaded to a threadpool (for heavy CPU consider a process pool).

## Sync vs Async: What Changes?
### Sync (`def`)
- Blocking operations stop the current worker until completion.
- In FastAPI, sync path functions run in a threadpool automatically.
- Simpler when dealing with non-async libraries.

### Async (`async def`)
- Use `await` for I/O-bound waits; frees the event loop to handle more requests.
- Enables concurrency with tools like `asyncio.gather`.
- Don’t call blocking functions directly — wrap them in a threadpool.

## Comparing Patterns
### Blocking I/O (bad in async)
```python
import time

async def handler():
    time.sleep(2)  # BAD: blocks event loop
    return {"ok": True}
```

### Non-blocking I/O (good)
```python
import asyncio

async def handler():
    await asyncio.sleep(2)  # GOOD: yields control
    return {"ok": True}
```

### Wrapping blocking code (good)
```python
from fastapi.concurrency import run_in_threadpool

async def handler():
    result = await run_in_threadpool(blocking_call, 2)
    return {"result": result}
```

### Run many I/O tasks concurrently
```python
results = await asyncio.gather(
    async_io_task(1.0),
    async_io_task(1.5),
    async_io_task(0.5),
)
```

## When to use `def` vs `async def`
- Use `async def` if:
  - You will `await` I/O (HTTP calls, DB calls with async drivers, `asyncio.sleep`).
  - You need concurrency across multiple I/O tasks (`asyncio.gather`).
- Use `def` if:
  - You are calling blocking libraries without async support.
  - Note: FastAPI automatically runs sync path functions in a threadpool.

## When to use async, sync, and multithreading (real-world examples)

- **Use async (`async def`) when your work is I/O-bound and awaitable**:
  - Example: Calling external REST APIs using an async client (e.g., httpx/async) and combining many requests with `asyncio.gather`.
  - Example: Handling WebSockets or server-sent events where the handler awaits incoming messages.
  - Example: Using async database drivers (e.g., asyncpg, SQLAlchemy 2.0 async engine) to execute queries without blocking the loop.
  - Why: Requests can proceed concurrently while awaiting network/disk operations, increasing throughput and lowering latency.

- **Use sync (`def`) when you must call blocking libraries and you don’t need fine-grained concurrency inside the handler**:
  - Example: Using a blocking SDK (legacy payment gateway, non-async ORM/driver) where you cannot `await`.
  - Example: Light CPU work plus a single blocking I/O call (e.g., read a file, call a blocking HTTP client) where simplicity matters.
  - Why: FastAPI runs sync path functions in a threadpool so the event loop stays responsive; code remains straightforward.

- **Use multithreading to offload blocking segments from async handlers**:
  - Example: In `async def`, wrap a blocking email/S3 client call using `await run_in_threadpool(send_email, ...)` so other requests aren’t stalled.
  - Example: Reading multiple large files or calling multiple blocking SDKs in parallel by scheduling several threadpool tasks.
  - Why: Threads prevent blocking the event loop when you cannot switch to async libraries.

- **Use multiprocessing for heavy CPU-bound work**:
  - Example: Image/video processing, PDF rendering, large JSON/XML parsing, ML inference on CPU.
  - Why: Processes bypass the GIL and can utilize multiple cores; queue heavy tasks to a process pool or a separate worker service.

## I/O-bound vs CPU-bound
- **I/O-bound**: Waiting on network/file/database. Prefer `async def` + `await` to maximize concurrency.
- **CPU-bound**: Heavy computation. Consider process pools or task queues; threads can help but are limited by the GIL. For small CPU tasks, offload to a threadpool to keep the loop responsive.

## Threading vs Async vs Processing
- **Async** excels at I/O concurrency with low overhead.
- **Threading** is useful when you must use blocking APIs or have light CPU work; it keeps the event loop unblocked.
- **Processing** is best for heavy CPU work to gain real parallelism.
- Combine approaches: `async def` handlers that offload blocking segments to a threadpool and heavy CPU to a process pool.

## Common Pitfalls
- Calling blocking functions inside `async def` without offloading.
- Mixing `time.sleep` and `await` incorrectly.
- Assuming `async` makes CPU work faster — it doesn’t; use processes for real parallelism.

## Practical Exercises
1. Hit `/async/await-one` and `/sync/noawait` simultaneously. Observe responsiveness.
2. Hit `/async/await-many` and confirm total time ~ max(task durations).
3. Compare `/async/wrap-blocking` vs `/async/bad-blocking` under concurrent load.

## Design Guidelines (from FastAPI docs)
- If you call libraries with `await`, declare path operations with `async def`.
- If you call blocking libraries, declare with `def` so FastAPI uses a threadpool.
- You can mix `def` and `async def` as needed; choose per endpoint’s needs.

## Further Reading
- FastAPI: Concurrency and async / await — [fastapi.tiangolo.com/async](https://fastapi.tiangolo.com/async/)

---

This folder provides a practical, minimal setup to understand how concurrency and async/await affect FastAPI performance and scalability.
