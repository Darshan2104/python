import asyncio
import aiohttp
import time
import json
from concurrent.futures import ThreadPoolExecutor
import threading

async def send_request_async(session, request_id):
    """Send a single request asynchronously"""
    url = "http://127.0.0.1:8001/process"
    payload = json.dumps({"text": f"test_request_{request_id}", "id": request_id})
    headers = {'Content-Type': 'application/json'}
    
    try:
        start_time = time.perf_counter()
        async with session.post(url, headers=headers, data=payload) as response:
            response_text = await response.text()
            end_time = time.perf_counter()
            return {
                "id": request_id,
                "status": response.status,
                "response": response_text,
                "duration": end_time - start_time
            }
    except Exception as e:
        return {
            "id": request_id,
            "status": "error",
            "response": str(e),
            "duration": 0
        }

def send_request_sync(request_id):
    """Send a single request synchronously (for ThreadPoolExecutor)"""
    import requests
    url = "http://127.0.0.1:8001/process"
    payload = json.dumps({"text": f"test_request_{request_id}", "id": request_id})
    headers = {'Content-Type': 'application/json'}
    
    try:
        start_time = time.perf_counter()
        response = requests.post(url, headers=headers, data=payload)
        end_time = time.perf_counter()
        return {
            "id": request_id,
            "status": response.status_code,
            "response": response.text,
            "duration": end_time - start_time
        }
    except Exception as e:
        return {
            "id": request_id,
            "status": "error",
            "response": str(e),
            "duration": 0
        }

async def test_async_load(total_requests=1000):
    """Test with async requests using aiohttp"""
    print(f"🚀 Starting async load test with {total_requests} requests...")
    
    start_time = time.perf_counter()
    
    async with aiohttp.ClientSession() as session:
        # Create all requests as tasks
        tasks = [send_request_async(session, i) for i in range(total_requests)]
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
    
    end_time = time.perf_counter()
    total_duration = end_time - start_time
    
    # Analyze results
    successful_requests = [r for r in results if r["status"] == 200]
    failed_requests = [r for r in results if r["status"] != 200]
    
    print(f"\n📊 Async Load Test Results:")
    print(f"Total requests: {total_requests}")
    print(f"Successful: {len(successful_requests)}")
    print(f"Failed: {len(failed_requests)}")
    print(f"Total time: {total_duration:.2f} seconds")
    print(f"Requests per second: {total_requests/total_duration:.2f}")
    
    if successful_requests:
        avg_response_time = sum(r["duration"] for r in successful_requests) / len(successful_requests)
        print(f"Average response time: {avg_response_time:.3f} seconds")
    
    return results

def test_sync_load(total_requests=1000):
    """Test with sync requests using ThreadPoolExecutor"""
    print(f"🔄 Starting sync load test with {total_requests} requests...")
    
    start_time = time.perf_counter()
    
    # Use ThreadPoolExecutor to send requests concurrently
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(send_request_sync, i) for i in range(total_requests)]
        results = [future.result() for future in futures]
    
    end_time = time.perf_counter()
    total_duration = end_time - start_time
    
    # Analyze results
    successful_requests = [r for r in results if r["status"] == 200]
    failed_requests = [r for r in results if r["status"] != 200]
    
    print(f"\n📊 Sync Load Test Results:")
    print(f"Total requests: {total_requests}")
    print(f"Successful: {len(successful_requests)}")
    print(f"Failed: {len(failed_requests)}")
    print(f"Total time: {total_duration:.2f} seconds")
    print(f"Requests per second: {total_requests/total_duration:.2f}")
    
    if successful_requests:
        avg_response_time = sum(r["duration"] for r in successful_requests) / len(successful_requests)
        print(f"Average response time: {avg_response_time:.3f} seconds")
    
    return results

def test_single_request():
    """Test a single request to verify the endpoint works"""
    print("🧪 Testing single request...")
    import requests
    
    url = "http://127.0.0.1:8001/process"
    payload = json.dumps({"text": "single_test", "id": "single"})
    headers = {'Content-Type': 'application/json'}
    
    try:
        start_time = time.perf_counter()
        response = requests.post(url, headers=headers, data=payload)
        end_time = time.perf_counter()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Duration: {end_time - start_time:.3f} seconds")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 FastAPI Queue Load Testing Tool")
    print("=" * 50)
    
    # # First, test if the server is running
    # if not test_single_request():
    #     print("❌ Server not responding. Make sure app.py is running on port 8001")
    #     return
    
    print("\n✅ Server is responding. Starting load tests...")
    
    # Test with async requests (more realistic for high concurrency)
    print("\n" + "="*50)
    await test_async_load(10000)
    
    # # Test with sync requests using ThreadPoolExecutor
    # print("\n" + "="*50)
    # test_sync_load(100)
    
    # print("\n🎯 Load testing completed!")
    # print("\n💡 Analysis:")
    # print("- The async queue in app.py should handle 1000 requests efficiently")
    # print("- With 4 workers, requests will be queued and processed in batches")
    # print("- Check the server console for worker processing logs")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())