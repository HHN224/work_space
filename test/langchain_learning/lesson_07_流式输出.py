# ============================================
# LangChain 第7课：流式输出（Streaming）
# ============================================
# 核心：.stream() 返回一个生成器，每次吐出一小段文字。
# 终端里用 print(chunk, end="", flush=True) 就能模拟打字机效果。
# ============================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"

llm = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.7)
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是技术博主，用轻松口吻解释概念。"),
    ("human", "用 100 字左右解释一下：{topic}")
])
chain = prompt | llm | StrOutputParser()


# --------------------------------------------
# 1. 普通调用 .invoke()：等全部生成完才一次性返回
# --------------------------------------------
print("=== 方式1：invoke() ===")
result = chain.invoke({"topic": "什么是 RAG"})
print(result)
print()


# --------------------------------------------
# 2. 流式调用 .stream()：生成一点吐一点
# --------------------------------------------
# 生成器（generator）的本质：不是一次性算完，而是算一段 yield 一段。
# 就像 streaming 看视频，边下载边播放，不用等整部下完。

print("=== 方式2：stream() ===")
for chunk in chain.stream({"topic": "什么是 RAG"}):
    print(chunk, end="", flush=True)  # end="" 不换行，flush=True 立即显示
print("\n")


# --------------------------------------------
# 3. 对比：感知首字延迟（First Token Latency）
# --------------------------------------------
# invoke() 的等待时间 = 模型思考时间 + 全部生成时间
# stream() 的等待时间 = 模型思考时间 + 第一个 token 的时间
# 用户会明显觉得 stream() "反应更快"，因为字马上开始蹦出来。

import time

print("=== 对比首字延迟 ===")

# invoke
start = time.time()
_ = chain.invoke({"topic": "向量数据库"})
t_invoke = time.time() - start

# stream（只测到第一个 chunk 出来的时间）
start = time.time()
for chunk in chain.stream({"topic": "向量数据库"}):
    t_stream = time.time() - start
    break  # 拿到第一个 chunk 就停

print(f"invoke() 首字可见耗时: {t_invoke:.2f}s（等全部）")
print(f"stream() 首字可见耗时: {t_stream:.2f}s（仅首字）")
print("结论：stream 让用户更早看到内容，体验更好。\n")


# --------------------------------------------
# 4. RAG Chain 的流式输出
# --------------------------------------------
# stream() 可以套在任何 Chain 上，包括 RAG。
# 但注意：检索（retriever.invoke）是同步的，stream 只负责 LLM 生成部分的流式。

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"local_files_only": True}
)
vectorstore = Chroma(
    persist_directory="db",
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "根据参考资料回答。"),
    ("human", "资料：\n{context}\n\n问题：{question}")
])
rag_chain = rag_prompt | llm | StrOutputParser()

question = "介绍一下你做过的项目"
docs = retriever.invoke(question)
context = "\n\n".join([d.page_content for d in docs])

print(f"=== RAG + stream() ===")
print(f"问题：{question}")
print("AI 回答：", end="", flush=True)
for chunk in rag_chain.stream({"context": context, "question": question}):
    print(chunk, end="", flush=True)
print("\n")

# --------------------------------------------
# 课后思考
# --------------------------------------------
# 1. 如果 model 的 temperature 很高（很随机），stream() 出来的字会不会一跳一跳的？
#    （提示：不会。token 是线性生成的，随机性体现在"选哪个 token"，不是输出顺序。）
# 2. 为什么 stream() 不能直接让"检索"也流式？
#    （提示：检索是数据库查询，结果是完整的文档块，没法"半个 chunk 半个 chunk"返回。）
# 3. 工程上怎么把 Python 的生成器接到 Web 前端的打字机效果？
#    （提示：SSE / WebSocket。这是后面 Flask/FastAPI 番外篇的内容。）
