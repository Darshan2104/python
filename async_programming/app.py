import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import Dict
import time
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import sqlite3
import json
from contextlib import asynccontextmanager

# Database configuration
DATABASE_PATH = "requests_tracker.db"
MAX_QUEUE_SIZE = 100000  # Limit each queue to 100K requests

app = FastAPI()
MAX_WORKERS = 4
# Create separate queues for each worker to avoid contention
worker_queues = [asyncio.Queue(maxsize=MAX_QUEUE_SIZE) for _ in range(MAX_WORKERS)]

THREADS_PER_WORKER = 1000
MAX_CONCURRENT_REQUESTS = MAX_WORKERS * THREADS_PER_WORKER

# Store processed results
processed_results = {}

# Database functions
def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY,
            text TEXT,
            worker_id INTEGER,
            status TEXT,
            created_at TIMESTAMP,
            queued_at TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            processing_time REAL,
            step1_result TEXT,
            step2_result TEXT,
            final_result TEXT,
            thread_id INTEGER,
            error_message TEXT
        )
    ''')
    
    # Create queue_metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queue_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP,
            total_queued INTEGER,
            worker_0_queue INTEGER,
            worker_1_queue INTEGER,
            worker_2_queue INTEGER,
            worker_3_queue INTEGER,
            active_threads INTEGER,
            processed_requests INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DATABASE_PATH}")

def save_request_to_db(request_data: Dict, worker_id: int):
    """Save request details to database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO requests 
            (id, text, worker_id, status, created_at, queued_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            request_data.get('id'),
            request_data.get('text', ''),
            worker_id,
            'queued',
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Database error saving request: {e}")

def update_request_status(request_id: str, status: str, **kwargs):
    """Update request status and additional fields"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Build dynamic update query
        fields = []
        values = []
        
        if 'started_at' in kwargs:
            fields.append('started_at = ?')
            values.append(kwargs['started_at'])
        
        if 'completed_at' in kwargs:
            fields.append('completed_at = ?')
            values.append(kwargs['completed_at'])
        
        if 'processing_time' in kwargs:
            fields.append('processing_time = ?')
            values.append(kwargs['processing_time'])
        
        if 'step1_result' in kwargs:
            fields.append('step1_result = ?')
            values.append(kwargs['step1_result'])
        
        if 'step2_result' in kwargs:
            fields.append('step2_result = ?')
            values.append(kwargs['step2_result'])
        
        if 'final_result' in kwargs:
            fields.append('final_result = ?')
            values.append(kwargs['final_result'])
        
        if 'thread_id' in kwargs:
            fields.append('thread_id = ?')
            values.append(kwargs['thread_id'])
        
        if 'error_message' in kwargs:
            fields.append('error_message = ?')
            values.append(kwargs['error_message'])
        
        fields.append('status = ?')
        values.append(status)
        values.append(request_id)
        
        query = f"UPDATE requests SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Database error updating request {request_id}: {e}")

def save_queue_metrics():
    """Save current queue metrics to database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        worker_queue_sizes = [q.qsize() for q in worker_queues]
        active_threads = sum(len(pool._threads) for pool in worker_thread_pools.values())
        
        cursor.execute('''
            INSERT INTO queue_metrics 
            (timestamp, total_queued, worker_0_queue, worker_1_queue, worker_2_queue, worker_3_queue, active_threads, processed_requests)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            sum(worker_queue_sizes),
            worker_queue_sizes[0],
            worker_queue_sizes[1],
            worker_queue_sizes[2],
            worker_queue_sizes[3],
            active_threads,
            len(processed_results)
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Database error saving metrics: {e}")

# Worker function to process tasks from the queue
def fun_1(v):
    time.sleep(2)  # Simulates a blocking operation
    return "fun_1"

def fun_2(v):
    time.sleep(1)  # Simulates another blocking operation
    return "fun_2"

# Create thread pools for each worker
worker_thread_pools = {}

async def worker(worker_id: int):
    """Worker that continuously pulls requests and submits them to thread pool"""
    print(f"🚀 Worker {worker_id} started with {THREADS_PER_WORKER} threads")
    
    # Create a dedicated thread pool for this worker
    thread_pool = ThreadPoolExecutor(max_workers=THREADS_PER_WORKER, 
                                   thread_name_prefix=f"Worker-{worker_id}")
    worker_thread_pools[worker_id] = thread_pool
    
    # Track active tasks for this worker
    active_tasks = set()
    
    try:
        while True:
            try:
                # Use get_nowait() to avoid blocking - workers can pull simultaneously
                data = worker_queues[worker_id].get_nowait()
            except asyncio.QueueEmpty:
                # If queue is empty, wait a tiny bit and try again
                await asyncio.sleep(0.001)
                continue
                
            if data is None:
                break
            
            # Submit the request to thread pool immediately without waiting
            # This allows the worker to continue pulling more requests
            task = asyncio.create_task(process_request_in_threadpool(data, worker_id, thread_pool))
            active_tasks.add(task)
            
            # Clean up completed tasks
            active_tasks = {t for t in active_tasks if not t.done()}
            
            print(f"📤 Worker {worker_id} submitted request {data.get('id', 'unknown')} to thread pool. Active tasks: {len(active_tasks)}")
            
    finally:
        # Wait for all active tasks to complete
        if active_tasks:
            await asyncio.gather(*active_tasks, return_exceptions=True)
        # Clean up thread pool
        thread_pool.shutdown(wait=True)
        print(f"🛑 Worker {worker_id} thread pool shutdown complete")

async def process_request_in_threadpool(data: Dict, worker_id: int, thread_pool: ThreadPoolExecutor):
    """Process a single request in the worker's thread pool"""
    request_id = data.get('id', 'unknown')
    
    try:
        # Update status to started
        update_request_status(request_id, 'processing', started_at=datetime.now().isoformat())
        
        result = await execute_task_with_retries(pipeline, data, worker_id, thread_pool)
        
        # Store the result with the request ID
        if "id" in data:
            processed_results[data["id"]] = result
        
        # Update status to completed
        update_request_status(
            request_id, 
            'completed',
            completed_at=datetime.now().isoformat(),
            processing_time=result.get('processing_time'),
            step1_result=result.get('step1_result'),
            step2_result=result.get('step2_result'),
            final_result=result.get('final_result'),
            thread_id=result.get('thread_id')
        )
        
        print(f"✅ Worker {worker_id} completed request {request_id}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        update_request_status(request_id, 'failed', error_message=error_msg)
        print(f"❌ Worker {worker_id} failed to process request {request_id}: {e}")
        return None

async def execute_task_with_retries(func, *args, retries=3):
    for attempt in range(retries):
        try:
            result = await func(*args)
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt + 1 == retries:
                print(f"Task failed after {retries} attempts.")
                raise
            await asyncio.sleep(1)

# Function to enqueue tasks - distribute across workers
async def process_request(data: Dict):
    # Distribute requests across workers using round-robin
    worker_id = hash(data.get('id', str(uuid.uuid4()))) % MAX_WORKERS
    
    # Check if this worker's queue is full
    if worker_queues[worker_id].qsize() >= MAX_QUEUE_SIZE:
        raise Exception(f"Worker {worker_id} queue is full")
    
    await worker_queues[worker_id].put(data)
    print(f"📥 Request {data.get('id', 'unknown')} routed to Worker {worker_id}")
    
    # Save to database
    save_request_to_db(data, worker_id)

# Your pipeline logic - now runs in a single thread per request
def pipeline_sync(data: Dict, worker_id: int):
    """Synchronous version of pipeline that runs in a single thread"""
    start_time = time.perf_counter()
    
    request_id = data["id"]
    text = data.get("text", "default_text")
    
    print(f"🔄 Worker {worker_id} processing request {request_id}: {text}")
    
    # Simulate some processing steps
    v = text
    
    # Step 1: Process with fun_1 (simulates some computation)
    result1 = fun_1(v)
    print(f"  ✅ Worker {worker_id} - Step 1 completed for {request_id}: {result1}")
    
    # Step 2: Process with fun_2 (simulates another computation)
    result2 = fun_2(v)
    print(f"  ✅ Worker {worker_id} - Step 2 completed for {request_id}: {result2}")
    
    # Step 3: Simulate additional processing
    time.sleep(0.5)  # Simulate additional processing
    processed_text = f"processed_{text}_{result1}_{result2}"
    print(f"  ✅ Worker {worker_id} - Step 3 completed for {request_id}: {processed_text}")
    
    end_time = time.perf_counter()
    processing_time = end_time - start_time
    
    result = {
        "request_id": request_id,
        "original_text": text,
        "step1_result": result1,
        "step2_result": result2,
        "final_result": processed_text,
        "processing_time": processing_time,
        "worker_id": worker_id,
        "thread_id": threading.current_thread().ident,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "optimization": "separate_queues_maximum_parallelism"
    }
    
    print(f"🎯 Worker {worker_id} - Request {request_id} completed in {processing_time:.3f}s")
    print(f"Processed: {data}")
    
    return result

async def pipeline(data: Dict, worker_id: int, thread_pool: ThreadPoolExecutor):
    """Async wrapper that submits the pipeline to the worker's thread pool"""
    # Submit the synchronous pipeline to the worker's thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(thread_pool, pipeline_sync, data, worker_id)
    return result

@app.post("/process")
async def process(data: Dict, background_tasks: BackgroundTasks):
    # Check total queue size across all workers
    total_queued = sum(q.qsize() for q in worker_queues)
    
    if total_queued >= MAX_QUEUE_SIZE * MAX_WORKERS:
        raise HTTPException(
            status_code=503, 
            detail=f"System overloaded. Total queued: {total_queued}, Max capacity: {MAX_QUEUE_SIZE * MAX_WORKERS}"
        )
    
    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())
    data["id"] = request_id
    
    print(f"📥 Received request {request_id}: {data}")
    
    # Add to background tasks
    background_tasks.add_task(process_request, data)
    
    return {
        "status": "accepted", 
        "request_id": request_id,
        "message": "Request queued for processing",
        "worker_assigned": hash(request_id) % MAX_WORKERS,
        "total_queued": total_queued,
        "max_capacity": MAX_QUEUE_SIZE * MAX_WORKERS,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status/{request_id}")
async def get_status(request_id: str):
    """Get the processing status and results for a specific request"""
    if request_id in processed_results:
        return {
            "request_id": request_id,
            "status": "completed",
            "result": processed_results[request_id]
        }
    else:
        # Check if it's still in any worker queue
        total_queue_size = sum(q.qsize() for q in worker_queues)
        return {
            "request_id": request_id,
            "status": "processing",
            "total_queue_size": total_queue_size,
            "message": "Request is still being processed or in queue"
        }

@app.get("/queue-status")
async def get_queue_status():
    """Get current queue and processing status"""
    active_threads = sum(len(pool._threads) for pool in worker_thread_pools.values())
    worker_queue_sizes = [q.qsize() for q in worker_queues]
    
    # Save metrics to database
    save_queue_metrics()
    
    return {
        "total_queue_size": sum(worker_queue_sizes),
        "worker_queue_sizes": worker_queue_sizes,
        "active_workers": MAX_WORKERS,
        "threads_per_worker": THREADS_PER_WORKER,
        "max_concurrent_requests": MAX_CONCURRENT_REQUESTS,
        "active_threads": active_threads,
        "processed_requests": len(processed_results),
        "max_queue_size_per_worker": MAX_QUEUE_SIZE,
        "total_max_capacity": MAX_QUEUE_SIZE * MAX_WORKERS,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/database/stats")
async def get_database_stats():
    """Get comprehensive database statistics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get request counts by status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM requests 
            GROUP BY status
        ''')
        status_counts = dict(cursor.fetchall())
        
        # Get recent queue metrics
        cursor.execute('''
            SELECT * FROM queue_metrics 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_metrics = cursor.fetchall()
        
        # Get processing time statistics
        cursor.execute('''
            SELECT 
                AVG(processing_time) as avg_time,
                MIN(processing_time) as min_time,
                MAX(processing_time) as max_time,
                COUNT(*) as total_completed
            FROM requests 
            WHERE status = 'completed'
        ''')
        time_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "request_status_counts": status_counts,
            "recent_queue_metrics": recent_metrics,
            "processing_time_stats": {
                "average_time": time_stats[0],
                "min_time": time_stats[1],
                "max_time": time_stats[2],
                "total_completed": time_stats[3]
            },
            "database_path": DATABASE_PATH,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

# Startup event to initialize worker pool
@app.on_event("startup")
async def startup_event():
    # Initialize database
    init_database()
    
    print(f"🚀 Starting {MAX_WORKERS} workers with {THREADS_PER_WORKER} threads each...")
    print(f"📊 Total concurrent processing capacity: {MAX_CONCURRENT_REQUESTS} requests")
    print(f"🔥 This will process {MAX_CONCURRENT_REQUESTS} requests simultaneously!")
    print(f"⚡ Workers will continuously pull requests and submit to thread pools!")
    print(f"🚀 Using separate queues per worker for maximum parallelism!")
    print(f"🎯 Round-robin distribution across {MAX_WORKERS} workers!")
    print(f"💾 SQLite database initialized for persistent tracking!")
    print(f"🛡️ Queue size limits: {MAX_QUEUE_SIZE} per worker ({MAX_QUEUE_SIZE * MAX_WORKERS} total)")
    
    for i in range(MAX_WORKERS):
        asyncio.create_task(worker(i))
    
    print(f"✅ {MAX_WORKERS} workers started successfully")

# Shutdown event to stop workers
@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down workers...")
    for q in worker_queues:
        await q.put(None)
    
    # Wait for all workers to finish
    await asyncio.sleep(2)
    print("✅ Workers shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

