---
主题: asyncio事件循环
分类: python
日期: 2026-06-15
---


## 一句话定义

asyncio是一个python标准库，提供了事件循环和协程的基础设施

## 我的理解

想要理解asyncio就必须先理解协程，协程是一种通过事件循环在单线程实现多任务并发的编程方式，让任务在执行IO等待时主动让出执行权，从而提升IO密集型任务单位时间的吞吐量。而asyncio编程中有两个比较重要的关键字，一个是async，另一个是await：asyncio是一个协程关键字，用来定义协程函数，调用协程函数会生成协程对象；await则是一个“可能需要让出执行权”的标记点，当await后面的任务阻塞时，会让出执行权，让事件循环先处理其他任务，等到阻塞结束了，再继续运行这个任务的剩下部分。

## 一个例子
```python
import asyncio
import time

# 模拟一个 IO 操作（比如网络请求）
async def fetch_data(url, delay):
    print(f"开始获取 {url}")
    await asyncio.sleep(delay)  # 模拟网络延迟，非阻塞
    print(f"完成获取 {url}")
    return f"数据-{url}"

async def main():
    urls = [("A", 2), ("B", 1), ("C", 3)]

    # 创建多个任务并发执行
    tasks = [fetch_data(url, delay) for url, delay in urls]

    start = time.time()
    results = await asyncio.gather(*tasks)  # 等待所有任务完成
    print(f"总耗时: {time.time() - start:.2f}s")
    print(f"结果: {results}")

asyncio.run(main())

输出：
开始获取 A
开始获取 B
开始获取 C
完成获取 B
完成获取 A
完成获取 C
总耗时: 3.01s          # 并发执行，总耗时 ≈ 最慢的那个
结果: ['数据-A', '数据-B', '数据-C']

同步版本对比（阻塞）：

import time

def fetch_sync(url, delay):
    time.sleep(delay)  # 阻塞整个线程
    return f"数据-{url}"

for url, delay in [("A", 2), ("B", 1), ("C", 3)]:
    fetch_sync(url, delay)  # 阻塞，一个接一个执行，总耗时 = 2+1+3 = 6秒
                                