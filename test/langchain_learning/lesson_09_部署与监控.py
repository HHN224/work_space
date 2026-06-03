# ============================================
# LangChain 第9课：部署与监控
# ============================================
# 核心：
#   1. 日志：记录每次调用的耗时、token消耗、异常
#   2. 容错：API超时、余额不足、网络抖动
#   3. 限流：防止单请求过长token
#   4. 指标：首token延迟、总耗时、错误率
# ============================================

import time
import json
import traceback
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.7,
    max_tokens=512,      # 限流：单次最多512 tokens，防止意外消耗
    request_timeout=15   # 限流：最多等15秒，防止挂死
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是技术助手，简洁回答。"),
    ("human", "{question}")
])
chain = prompt | llm | StrOutputParser()

# 简单的内存日志存储（生产环境应写到文件或Prometheus）
logs = []


def log_call(func_name, question, start_time, success, result_or_error, first_token_time=None):
    """记录一次调用的完整指标。"""
    end_time = time.time()
    record = {
        "timestamp": datetime.now().isoformat(),
        "function": func_name,
        "question": question,
        "total_duration": round(end_time - start_time, 3),
        "first_token_latency": round(first_token_time - start_time, 3) if first_token_time else None,
        "success": success,
        "result": result_or_error if success else None,
        "error": str(result_or_error) if not success else None
    }
    logs.append(record)
    # 实时打印到控制台
    print(f"\n[LOG] {record['timestamp']}")
    print(f"      函数: {func_name}")
    print(f"      问题: {question}")
    print(f"      总耗时: {record['total_duration']}s")
    if record['first_token_latency']:
        print(f"      首字延迟: {record['first_token_latency']}s")
    print(f"      状态: {'✅ 成功' if success else '❌ 失败'}")
    if not success:
        print(f"      错误: {record['error']}")


def safe_invoke(question):
    """
    安全调用：带异常捕获、超时处理、日志记录。
    生产环境中，这是每个对外接口的标配包装。
    """
    start = time.time()
    first_token_time = None

    try:
        # stream() 方式调用，同时记录首token时间
        chunks = []
        for chunk in chain.stream({"question": question}):
            if first_token_time is None:
                first_token_time = time.time()
            chunks.append(chunk)

        result = "".join(chunks)
        log_call("safe_invoke", question, start, True, result, first_token_time)
        return result

    except Exception as e:
        # 捕获一切异常：网络超时、余额不足、模型下线、格式错误...
        error_detail = traceback.format_exc()
        log_call("safe_invoke", question, start, False, error_detail)
        return f"[服务异常] 暂时无法处理，请稍后重试。详细错误：{str(e)}"


# --------------------------------------------
# 演示1：正常调用
# --------------------------------------------
print("=== 演示1：正常调用 ===")
r1 = safe_invoke("什么是 Docker？")
print(f"回答：{r1}\n")


# --------------------------------------------
# 演示2：模拟超时/异常
#    修改 llm 的 request_timeout=0.001，让请求必然超时
#    观察异常捕获和日志记录效果
# --------------------------------------------
print("=== 演示2：模拟超时异常 ===")
llm_fast_fail = ChatOpenAI(
    model="deepseek-chat",
    api_key=API_KEY,
    base_url=BASE_URL,
    request_timeout=0.001  # 故意设成 1ms，必定超时
)
chain_fast_fail = prompt | llm_fast_fail | StrOutputParser()

def safe_invoke_fast_fail(question):
    start = time.time()
    try:
        result = chain_fast_fail.invoke({"question": question})
        log_call("safe_invoke_fast_fail", question, start, True, result)
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        log_call("safe_invoke_fast_fail", question, start, False, error_detail)
        return f"[服务异常] {str(e)}"

r2 = safe_invoke_fast_fail("什么是 Kubernetes？")
print(f"回答：{r2}\n")


# --------------------------------------------
# 演示3：输出监控报表
# --------------------------------------------
print("=== 演示3：监控报表 ===")
success_count = sum(1 for log in logs if log["success"])
total_count = len(logs)
avg_duration = sum(log["total_duration"] for log in logs) / total_count if total_count else 0

print(f"总调用次数: {total_count}")
print(f"成功次数: {success_count}")
print(f"失败次数: {total_count - success_count}")
print(f"平均耗时: {round(avg_duration, 3)}s")
print(f"错误率: {round((total_count - success_count) / total_count * 100, 1)}%")

# 如果需要，可以把 logs 列表写成 JSON 文件持久化
# with open("logs.json", "w", encoding="utf-8") as f:
#     json.dump(logs, f, ensure_ascii=False, indent=2)

# --------------------------------------------
# 课后思考
# --------------------------------------------
# 1. 生产环境如何把日志发到 Grafana/Prometheus？
#    （提示：把 log_call 改成 pushgateway 或写入文件由 fluentd 采集。）
# 2. 如何实现"熔断"——如果连续失败 5 次，自动停止服务并报警？
#    （提示：在 log_call 里统计最近 N 次的 success 率，低于阈值则触发报警。）
# 3. max_tokens 和 request_timeout 是最后一道防线：
#    即使 Prompt 注入攻击导致异常长输出，max_tokens 也会强制截断，保护余额。
