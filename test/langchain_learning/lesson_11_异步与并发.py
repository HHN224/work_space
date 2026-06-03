# ============================================
# LangChain 第11课：异步与并发
# ============================================
# 核心问题：LLM 调用是网络 I/O，同步阻塞会浪费大量等待时间。
# 解决：
#   1. async/await + ainvoke() —— 并发多个请求，减少总耗时
#   2. Celery —— 后台任务队列，Web 接口"提交即返回"
# ============================================
# 课前准备：
#   pip install celery
# ============================================

import asyncio
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"

prompt = ChatPromptTemplate.from_messages([
    ("system", "回答控制在20字以内。"),
    ("human", "{question}")
])
llm = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.7)
chain = prompt | llm | StrOutputParser()

questions = ["什么是Docker", "什么是Kubernetes", "什么是CI/CD"]


# --------------------------------------------
# 1. 同步阻塞：串行执行
#    每次 invoke() 都会阻塞，等服务器返回后才能发下一个请求。
#    3 个问题串行 ≈ 3 倍单问耗时。
# --------------------------------------------
print("=== 1. 同步串行 ===")
start = time.time()
for q in questions:
    r = chain.invoke({"question": q})
    print(f"  {q}: {r}")
print(f"总耗时: {time.time() - start:.2f}s\n")


# --------------------------------------------
# 2. 异步并发：同时发出 3 个请求
#    ainvoke() 是异步版本，await 时不会阻塞事件循环。
#    asyncio.gather() 把多个异步任务捆在一起并发执行。
#    总耗时 ≈ 最慢的那个请求，而不是累加。
# --------------------------------------------
print("=== 2. 异步并发 ===")

async def ask(question):
    r = await chain.ainvoke({"question": question})
    return question, r

async def main():
    start = time.time()
    # gather 同时启动所有任务，网络等待期互相不阻塞
    results = await asyncio.gather(*[ask(q) for q in questions])
    for q, r in results:
        print(f"  {q}: {r}")
    print(f"总耗时: {time.time() - start:.2f}s\n")

asyncio.run(main())


# --------------------------------------------
# 3. Celery：后台任务队列
#    解决的是另一个维度的问题：
#      Web 接口收到请求 → 不能让用户干等 5 秒 → 立即返回"任务已提交"+任务ID
#      → LLM 调用在后台 worker 里慢慢跑 → 前端轮询或 WebSocket 拿结果
#    这样 Flask/Django 进程不会被长任务占满。
# --------------------------------------------
print("=== 3. Celery 后台任务 ===")

try:
    from celery import Celery

    # broker='memory://' 是内存模式，教学用，无需安装 Redis。
    # backend='cache+memory://' 也是内存模式，用于存储任务状态和结果，教学用。
    # 生产环境应换成 redis://localhost:6379/0
    celery_app = Celery('tasks', broker='memory://', backend='cache+memory://')

    @celery_app.task
    def llm_task(question):
        """这个函数会在 Celery Worker 进程里执行，不在 Web 主进程里。"""
        return chain.invoke({"question": question})

    print("【提交 3 个任务到队列】")
    start = time.time()
    jobs = [llm_task.delay(q) for q in questions]
    print(f"提交耗时: {time.time() - start:.3f}s (几乎瞬时)")
    print(f"任务IDs: {[j.id for j in jobs]}")

    print("\n【检查任务状态】")
    for i, j in enumerate(jobs):
        print(f"  任务{i+1}: {j.status}")

    if jobs[0].status == "PENDING":
        print("\n提示：当前没有 Celery Worker 在运行，任务处于排队状态。")
        print("如需真正执行，请在另一个终端运行：")
        print("  celery -A lesson_11_异步与并发 worker --pool=solo --loglevel=info")
        print("上述代码展示了完整的集成模式：Web 层只负责 delay() 提交，")
        print("真正的 LLM 调用在独立 worker 进程中完成，Web 进程零阻塞。")
    else:
        print("\n【获取结果】")
        for j in jobs:
            print(f"结果: {j.get(timeout=30)}")

except ImportError:
    print("未安装 celery，跳过。如需运行：pip install celery")

# --------------------------------------------
# 课后思考
# --------------------------------------------
# 1. 为什么异步能提速？
#    因为网络 I/O 等待时（等服务器返回），CPU 是空闲的。
#    async 让 Python 趁这个空档去发下一个请求，而不是傻等。
#
# 2. ainvoke() 和 invoke() 返回的结果格式完全一样吗？
#    是的，只是调用方式不同。一个是 await，一个是直接调。
#
# 3. Celery 比 async 重得多，为什么还要用？
#    async 解决的是"等待时别闲着"；
#    Celery 解决的是"任务太重/太长，不能放在 Web 进程里"。
#    它还自带重试、定时任务、监控、多机分布式，这些是 async 没有的。
#
# 4. Flask 怎么接 async？
#    Flask 2.0+ 支持 async 视图：
#      @app.route("/ask")
#      async def ask():
#          result = await chain.ainvoke(...)
#          return jsonify(result)
