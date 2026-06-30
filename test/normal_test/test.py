import asyncio
import random
import time

async def download_file(file_number):
    print(f"Downloading file {file_number}...")
    await asyncio.sleep(random.uniform(1.0, 3.0))  # Simulate download time

async def test(number):
    start_time = time.time()
    await download_file(number)  # Simulate some work
    end_time = time.time()
    print(f"Test {number} completed in {end_time - start_time:.2f} seconds")

async def multiple_tests():
    start_time = time.time()
    tasks = [test(i) for i in range(1, 6)]
    await asyncio.gather(*tasks)
    end_time = time.time()
    print(f"All tests completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(multiple_tests())

#孩子们还是打卡，期末太忙了根本没产出