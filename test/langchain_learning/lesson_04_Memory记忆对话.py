# ============================================
# LangChain 第4课：Memory —— 让 AI 记住对话历史
# ============================================
# 核心问题：默认情况下，每次 .invoke() 都是独立的，AI 不知道你之前说过什么。
# 解决：用 RunnableWithMessageHistory 自动把历史消息拼进 Prompt。
# ============================================

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"

llm = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.7)
parser = StrOutputParser()

# --------------------------------------------
# 1. Prompt 模板里留一个"历史消息插槽"
# --------------------------------------------
# MessagesPlaceholder 会自动填入之前的对话记录。
# 它告诉 LangChain："history 变量不是一条消息，而是很多条消息"。
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的助手。请根据上下文回答问题。"),
    MessagesPlaceholder(variable_name="history"),  # ← 历史插入点
    ("human", "{input}")
])

chain = prompt | llm | parser

# --------------------------------------------
# 2. 包装成带记忆的 Chain
# --------------------------------------------
# 用一个字典保存不同用户的对话历史，key 是 session_id。
# 实际项目中这里通常连 Redis / 数据库，而不是内存字典。
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# --------------------------------------------
# 3. 运行演示
# --------------------------------------------
config = {"configurable": {"session_id": "user-001"}}

print(">>> 第1轮")
r1 = chain_with_memory.invoke({"input": "你好，我叫小明，我喜欢Python"}, config=config)
print(f"AI: {r1}\n")

print(">>> 第2轮（AI 应该记得我叫小明）")
r2 = chain_with_memory.invoke({"input": "我叫什么名字？我喜欢什么语言？"}, config=config)
print(f"AI: {r2}\n")

print(">>> 第3轮（换用户 user-002，AI 不认识小明）")
config2 = {"configurable": {"session_id": "user-002"}}
r3 = chain_with_memory.invoke({"input": "我叫什么名字？"}, config=config2)
print(f"AI: {r3}")

# --------------------------------------------
# 课后思考
# --------------------------------------------
# 1. 如果对话很长（比如 50 轮），把所有历史都塞进 Prompt 会超出模型长度限制。
#    怎么办？（提示：下次课学 Token 限制和历史裁剪。）
# 2. 现在历史存在内存里，程序重启就丢了。如果要持久化，可以把 ChatMessageHistory
#    换成 RedisChatMessageHistory，或者自己用 SQLite/JSON 文件存。
# 3. 注意看第3轮：不同的 session_id 对应独立的记忆。这正是 Web 应用里
#    "每个用户只能看到自己的对话历史" 的实现基础。
