# ============================================
# LangChain 第10课：毕业项目 —— 智能简历问答助手
# ============================================
# 把前9课的所有能力串成一个完整应用：
#   RAG（读简历） + Memory（多轮对话） + Tools（计算年限）
#   + Streaming（流式输出） + Fallback（故障转移） + 监控日志
# 运行后，在终端里直接和 AI 对话，输入 exit 退出。
# ============================================

import os
import time
import uuid
from datetime import datetime

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage


API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"
PERSIST_DIR = "db"
RESUME_FILE = "data/resume.txt"

# ============================================
# 1. 初始化各组件
# ============================================

# LLM 主备
llm = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.7, max_tokens=1024, request_timeout=30)
llm_backup = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.7, max_tokens=1024, request_timeout=30)

# 向量库（简历 RAG）
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5", model_kwargs={"local_files_only": True})
if os.path.exists(PERSIST_DIR):
    vectorstore = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
else:
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("[系统] 首次运行，正在构建简历向量库...")
    loader = TextLoader(RESUME_FILE, encoding="utf-8")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=PERSIST_DIR)
    print(f"[系统] 向量库构建完成，共 {len(chunks)} 个片段\n")

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 带记忆的对话 Chain
prompt_chat = ChatPromptTemplate.from_messages([
    ("system", "你是李明的智能简历助手，基于简历资料和对话历史回答问题。如果问题与简历无关，可以闲聊但需说明。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain_chat_raw = prompt_chat | llm | StrOutputParser()

session_store = {}
def get_history(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

chain_chat = RunnableWithMessageHistory(
    chain_chat_raw,
    get_history,
    input_messages_key="input",
    history_messages_key="history"
)

# RAG Chain（基于简历）
prompt_rag = ChatPromptTemplate.from_messages([
    ("system", "根据以下简历资料回答问题。如果资料里没有答案，请明确说明。"),
    ("human", "简历资料：\n{context}\n\n问题：{question}")
])
chain_rag = prompt_rag | llm | StrOutputParser()

# Fallback 包装
chain_rag_safe = chain_rag.with_fallbacks([prompt_rag | llm_backup | StrOutputParser()])


# ============================================
# 2. 工具定义
# ============================================

@tool
def work_experience_years() -> str:
    """计算李明的工作年限。不需要参数，直接返回结果。"""
    # 根据简历：2020-2022 星辰网络（2年），2022-至今 未来科技（约3年）
    return "李明从 2020 年开始工作，至今已有约 5 年工作经验。"


# ============================================
# 3. 监控日志
# ============================================

logs = []

def log(question, mode, success, duration, error=None):
    record = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "question": question,
        "mode": mode,
        "success": success,
        "duration": round(duration, 2),
        "error": error
    }
    logs.append(record)


# ============================================
# 4. 主交互循环
# ============================================

def main():
    session_id = str(uuid.uuid4())
    print("=" * 50)
    print("🎓 智能简历问答助手（命令行版）")
    print("=" * 50)
    print("功能：")
    print("  - 问简历相关问题（RAG）：'你做过什么项目？'")
    print("  - 多轮闲聊（Memory）：'刚才说的那个项目详细讲讲'")
    print("  - 工具调用：'你工作几年了？' → 自动调用 work_experience_years")
    print("  - 输入 'exit' 退出，输入 'logs' 查看监控")
    print("=" * 50)

    while True:
        user_input = input("\n你: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("再见！")
            break
        if user_input.lower() == "logs":
            print_monitor()
            continue

        # 路由决策：简单规则判断
        mode = "chat"
        if any(k in user_input for k in ["项目", "技术", "经验", "简历", "工作", "公司", "教育"]):
            mode = "rag"
        if any(k in user_input for k in ["几年", "年限", "多久"]):
            mode = "tool"

        start = time.time()

        try:
            if mode == "tool":
                # 工具调用：直接执行并给出自然语言回答
                tool_result = work_experience_years.invoke({})
                # 下面用 LLM 把工具结果包装成自然语言
                tool_prompt = f"用户问：{user_input}\n工具返回：{tool_result}\n请用一句话回答用户。"
                answer = llm.invoke(tool_prompt).content
                print(f"AI: {answer}")
                log(user_input, "tool", True, time.time() - start)

            elif mode == "rag":
                # RAG 模式：检索简历 → 流式生成
                docs = retriever.invoke(user_input)
                context = "\n\n".join([d.page_content for d in docs])

                print("AI: ", end="", flush=True)
                full_answer = []
                for chunk in chain_rag_safe.stream({"context": context, "question": user_input}):
                    print(chunk, end="", flush=True)
                    full_answer.append(chunk)
                print()
                log(user_input, "rag", True, time.time() - start)

            else:
                # 通用对话模式：带记忆
                print("AI: ", end="", flush=True)
                full_answer = []
                for chunk in chain_chat.stream({"input": user_input}, config={"configurable": {"session_id": session_id}}):
                    print(chunk, end="", flush=True)
                    full_answer.append(chunk)
                print()
                log(user_input, "chat", True, time.time() - start)

        except Exception as e:
            print(f"AI: [服务异常] {e}")
            log(user_input, mode, False, time.time() - start, str(e))


def print_monitor():
    print("\n" + "=" * 50)
    print("📊 监控日志")
    print("=" * 50)
    if not logs:
        print("暂无记录")
        return
    for record in logs:
        status = "✅" if record["success"] else "❌"
        print(f"[{record['time']}] {status} [{record['mode']}] ({record['duration']}s) {record['question']}")
    total = len(logs)
    success = sum(1 for r in logs if r["success"])
    avg = sum(r["duration"] for r in logs) / total
    print(f"\n总计: {total} 次 | 成功: {success} | 失败: {total - success} | 平均耗时: {round(avg, 2)}s")
    print("=" * 50)


if __name__ == "__main__":
    main()
