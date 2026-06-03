# ============================================
# LangChain 第6课：Flask × LangChain —— 封装 REST API
# ============================================
# 目标：把前几课的 Chain 变成 Web 接口，让前端/其他系统能调用
# 前提：你已经会 Flask 基础（路由、request.get_json()）
# ============================================

from flask import Flask, request, jsonify, redirect
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
import uuid

app = Flask(__name__)

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# --------------------------------------------
# CORS：允许浏览器前端直接调用
# --------------------------------------------
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --------------------------------------------
# 全局初始化（Flask 启动时只加载一次）
# --------------------------------------------
llm = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.7)

# 1) 带记忆的对话 Chain
prompt_chat = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的助手。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain_chat_raw = prompt_chat | llm | StrOutputParser()

# 内存中的会话历史存储（生产环境应换 Redis/SQLite）
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

# 2) RAG 问答 Chain（基于简历文档）
# 提示：如果你把 data/resume.txt 换成了自己的真实简历，
#       请删除 db/ 文件夹，然后重新启动 Flask，系统会自动重建向量库。
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"local_files_only": True}
)
DB_DIR = r"C:\Users\OMEN\Desktop\OpenCode\test\langchain_learning\db"
RESUME_FILE = r"C:\Users\OMEN\Desktop\OpenCode\test\langchain_learning\data\resume.txt"

if os.path.exists(DB_DIR):
    # 已有向量库，直接加载
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    print("[系统] 加载已有向量库 db/")
else:
    # 首次运行：读取简历 → 切分 → 向量化 → 持久化
    print("[系统] 首次运行，正在基于 resume.txt 构建向量库，请稍候...")
    loader = TextLoader(RESUME_FILE, encoding="utf-8")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(
        chunks, embeddings, persist_directory=DB_DIR
    )
    print(f"[系统] 向量库构建完成，共 {len(chunks)} 个片段")

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

prompt_rag = ChatPromptTemplate.from_messages([
    ("system", "你是知识库助手，根据参考资料回答。资料里没有就明说。"),
    ("human", "参考资料：\n{context}\n\n问题：{question}")
])
chain_rag = prompt_rag | llm | StrOutputParser()


# --------------------------------------------
# 根路由：自动跳转到前端页面
# --------------------------------------------
@app.route("/")
def index():
    return redirect("/static/index.html")


# --------------------------------------------
# API 1：通用对话（带记忆）
# POST /chat
# Body: {"message": "你好", "session_id": "可选，不传则自动创建"}
# --------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))

    # 调用带记忆的 Chain
    answer = chain_chat.invoke(
        {"input": user_msg},
        config={"configurable": {"session_id": session_id}}
    )

    return jsonify({
        "session_id": session_id,
        "reply": answer
    })


# --------------------------------------------
# API 2：知识库问答（RAG）
# POST /ask
# Body: {"question": "什么是 GIL？"}
# --------------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")

    # 检索
    docs = retriever.invoke(question)
    context = "\n\n".join([d.page_content for d in docs])

    # 生成
    answer = chain_rag.invoke({"context": context, "question": question})

    return jsonify({
        "question": question,
        "answer": answer,
        "sources": [d.page_content[:100] + "..." for d in docs]
    })


if __name__ == "__main__":
    print("=" * 50)
    print("Flask 服务启动")
    print("请在浏览器打开：http://127.0.0.1:5000/")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
