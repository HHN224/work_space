# ============================================
# LangChain 第3课：RAG 基础（持久化版）
# 目标：让 AI 先读你的文档，再基于文档内容回答问题
# 改进：向量库持久化到本地，首次生成后秒加载
# ============================================
# 课前准备（如未安装请运行）：
#   pip install langchain-community langchain-text-splitters chromadb langchain-huggingface
# ============================================

import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"
PERSIST_DIR = "db"

# --------------------------------------------
# 3. 向量化并入库（持久化版）
#    首次：读取文件 → 切分 → 向量化 → 存入本地 db 文件夹
#    后续：直接加载本地 db 文件夹，跳过前面所有步骤，秒开
# --------------------------------------------
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

if os.path.exists(PERSIST_DIR):
    vectorstore = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )
else:
    # 首次运行才走这里
    loader = TextLoader("data/python_faq.txt", encoding="utf-8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
    chunks = splitter.split_documents(docs)

    print(f"首次运行：文档被切成了 {len(chunks)} 个片段\n")
    for i, chunk in enumerate(chunks):
        print(f"--- 片段 {i} ---")
        print(chunk.page_content[:120] + "...\n")

    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=PERSIST_DIR
    )

# --------------------------------------------
# 4. 检索
# --------------------------------------------
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

question = "为什么 Python 多线程不能加速 CPU 密集型任务？"
retrieved_docs = retriever.invoke(question)

print(f"用户问题：{question}\n")
print(f"检索到 {len(retrieved_docs)} 个相关片段：")
context = ""
for i, doc in enumerate(retrieved_docs):
    print(f"[{i+1}] {doc.page_content[:100]}...")
    context += doc.page_content + "\n\n"

# --------------------------------------------
# 5. 构建 RAG Prompt
# --------------------------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的 Python 技术助手。请根据提供的参考资料回答用户问题，如果资料里没有答案，请明确说明。"),
    ("human", "参考资料：\n{context}\n\n用户问题：{question}")
])

# --------------------------------------------
# 6. 调用 AI 生成回答
# --------------------------------------------
llm = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.3)
chain = prompt | llm | StrOutputParser()

answer = chain.invoke({"context": context, "question": question})
print(f"\nAI 回答：\n{answer}")

# --------------------------------------------
# 课后思考
# --------------------------------------------
# 1. 如果你把 chunk_size 改大（比如 500），检索效果会怎样？为什么？
# 2. 如果用户问了一个文档里没有的问题（比如"什么是 Flask"），AI 会怎么回答？
# 3. 如果要支持多文件、更新文件后重新入库，应该怎么做？（提示：删除 db 文件夹即可重新生成）
