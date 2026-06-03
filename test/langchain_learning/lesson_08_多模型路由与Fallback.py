# ============================================
# LangChain 第8课：多模型路由与 Fallback
# ============================================
# 核心：
#   1. Fallback —— 主模型挂了，自动切到备用模型，保证服务不中断。
#   2. Router —— 根据问题特征，自动选择"便宜模型"或"强模型"。
# ============================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是技术助手，简洁回答。"),
    ("human", "{question}")
])

# --------------------------------------------
# 1. Fallback（故障转移）
#    主模型故意用错误 Key，模拟服务故障。
#    备用模型用正确 Key，确保最终能成功。
#    错误 Key 会立即返回 401，不消耗 Token 余额。
# --------------------------------------------

llm_primary = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-wrong-key-simulate-failure",  # 故意错误，模拟主模型宕机
    base_url=BASE_URL,
    temperature=0.7
)

llm_backup = ChatOpenAI(
    model="deepseek-chat",
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.7
)

chain_primary = prompt | llm_primary | StrOutputParser()
chain_backup = prompt | llm_backup | StrOutputParser()

# with_fallbacks 是 LangChain 原生机制：
# 先跑 primary，如果抛异常，按顺序跑 fallbacks 里的备胎。
chain_with_fallback = chain_primary.with_fallbacks([chain_backup])

print("=== 1. Fallback 演示 ===")
print("主模型 Key 错误，预期会失败一次，然后自动切到备用模型。\n")

result = chain_with_fallback.invoke({"question": "你好，验证一下服务是否正常"})
print(f"最终回答：{result}\n")


# --------------------------------------------
# 2. Router（智能路由）
#    根据问题复杂度选择不同模型：
#    - 简单问题（闲聊、基础概念）→ deepseek-chat（便宜、快）
#    - 复杂问题（代码、推理、数学）→ deepseek-reasoner（强、慢、贵）
# --------------------------------------------

llm_chat = ChatOpenAI(
    model="deepseek-chat",
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.7
)

llm_reasoner = ChatOpenAI(
    model="deepseek-reasoner",
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.7
)

chain_chat = prompt | llm_chat | StrOutputParser()
chain_reasoner = prompt | llm_reasoner | StrOutputParser()


def route_question(data: dict) -> str:
    """
    路由规则：根据问题内容判断复杂度。
    返回字符串 key，对应下面字典里的 chain。
    """
    q = data.get("question", "")
    keywords_complex = ["代码", "bug", "调试", "算法", "推理", "证明", "分析", "优化"]
    if any(k in q for k in keywords_complex):
        return "complex"
    return "simple"


# RunnableLambda 把普通函数包装成 Runnable，可以用在 LCEL 链里。
router = RunnableLambda(route_question)

# {"simple": chainA, "complex": chainB} 这种写法是 LCEL 的 "映射路由"：
# router 返回 "simple" → 自动走 chain_chat；返回 "complex" → 自动走 chain_reasoner。
chain_router = router | {
    "simple": chain_chat,
    "complex": chain_reasoner
}

print("=== 2. Router 演示 ===")

questions = [
    "今天天气怎么样？",                      # 预期走 simple
    "帮我分析一下这段代码的性能瓶颈",        # 预期走 complex
]

for q in questions:
    route = route_question({"question": q})
    print(f"\n问题：{q}")
    print(f"路由决策：{route}")
    result = chain_router.invoke({"question": q})
    print(f"回答：{result[:80]}...")

# --------------------------------------------
# 课后思考
# --------------------------------------------
# 1. 生产环境中，fallback 的触发条件可以更精细：
#    不只是"异常"，还可以是"响应时间超过 3 秒"或"返回内容包含'服务繁忙'"等。
# 2. Router 的规则可以做得更智能：
#    先用一个极便宜的小模型（或正则规则）判断问题类型，再决定发给哪个大模型。
#    这比直接把问题发给大模型判断要省 90% 成本。
# 3. 你可以把 Fallback + Router 组合起来：
#    先路由选模型 → 该模型挂了 → fallback 到同类型的备胎。
