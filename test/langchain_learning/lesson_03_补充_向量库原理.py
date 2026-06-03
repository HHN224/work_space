# ============================================
# 补充课：向量数据库原理揭秘
# 目标：看清 db/ 文件夹里到底存了什么，理解检索的本质
# ============================================
# 不需要 API Key，纯本地探索
# ============================================

import os
import sqlite3

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

PERSIST_DIR = "db"

# --------------------------------------------
# 1. 加载已有的向量库
# --------------------------------------------
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)

# --------------------------------------------
# 2. 看看 SQLite 里存的原始数据
#    Chroma 的元数据、文本内容都存在 chroma.sqlite3 里
# --------------------------------------------
conn = sqlite3.connect(f"{PERSIST_DIR}/chroma.sqlite3")
cursor = conn.cursor()

# 获取文档片段内容和对应 ID
# 注意：Chroma 新版用 embedding_fulltext_search_content (id + c0) 存储全文
cursor.execute("SELECT id, c0 FROM embedding_fulltext_search_content")
rows = cursor.fetchall()

print("=== SQLite 里存的文本片段 ===")
for row in rows:
    doc_id, text = row
    print(f"ID: {doc_id}")
    print(f"文本: {text[:80]}...\n")

conn.close()

# --------------------------------------------
# 3. 向量到底是什么？把文字变成数字
# --------------------------------------------
# Embedding 模型的本质：一个函数 f(text) → [0.1, -0.3, 0.8, ...]
# 这个数组有 768 个数字（维度），每个数字叫一个"维度"
# "Python 的 GIL" 和 "多线程" 这两个概念相近，它们的 768 个数字也会很相近

sample_text = "Python 的 GIL 让多线程无法利用多核"
vec = embeddings.embed_query(sample_text)

print(f"=== 一句话变成了什么 ===")
print(f"原文: {sample_text}")
print(f"维度: {len(vec)} 维")
print(f"前 10 个数字: {vec[:10]}")
print(f"每个数字都是 float，范围通常在 -1 到 1 之间\n")

# --------------------------------------------
# 4. 检索的本质：算距离
#    把用户问题也变成 768 维向量，然后和库里所有片段的向量比"远近"
#    越近 = 语义越相关
# --------------------------------------------

q1 = "为什么 Python 多线程不能加速 CPU 任务？"
q2 = "列表和元组有什么区别？"

v1 = embeddings.embed_query(q1)
v2 = embeddings.embed_query(q2)

# 我们手动算一下 q1 和一个 GIL 片段的相似度
gil_text = "Python 的 GIL（全局解释器锁）：GIL 是 CPython 解释器中的一个机制，它确保同一时刻只有一个线程在执行 Python 字节码。这意味着多线程程序在 CPU 密集型任务上无法利用多核优势。"
vgil = embeddings.embed_query(gil_text)

# 余弦相似度：两个向量的夹角越小，值越接近 1
import numpy as np

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

sim_q1_gil = cosine_similarity(v1, vgil)
sim_q2_gil = cosine_similarity(v2, vgil)

print("=== 检索的本质：比距离 ===")
print(f"问题1: {q1}")
print(f"  → 与 GIL 片段的相似度: {sim_q1_gil:.4f}")
print(f"问题2: {q2}")
print(f"  → 与 GIL 片段的相似度: {sim_q2_gil:.4f}")
print(f"\n结论：问题1和 GIL 片段更接近，所以检索时会优先返回它。\n")

# --------------------------------------------
# 5. 看看 db/ 文件夹的文件结构
# --------------------------------------------
print("=== 本地文件结构 ===")
for root, dirs, files in os.walk(PERSIST_DIR):
    level = root.replace(PERSIST_DIR, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        filepath = os.path.join(root, file)
        size = os.path.getsize(filepath)
        print(f"{subindent}{file} ({size:,} bytes)")

print("""
文件说明：
- chroma.sqlite3: 存文本内容、ID、配置（纯 SQLite 数据库）
- data_level0.bin: 存 768 维向量数组（二进制浮点数，一行一个向量）
- header.bin / length.bin: 向量的索引和长度信息（告诉系统每段向量占多少字节）
""")

# --------------------------------------------
# 课后总结（注释形式）
# --------------------------------------------
# 向量数据库的 3 步原理：
# 1. 嵌入（Embed）：f("多线程") → [0.12, -0.05, 0.88, ...]   （768个float）
# 2. 存储（Store）：把这些数字数组存入二进制文件 + SQLite 元数据
# 3. 检索（Search）：把用户问题也变成数组，算和所有片段的"距离"，返回最近的 k 个
#
# 为什么快？
# - 不需要逐字匹配，不需要理解语法
# - 纯数学计算：两个数组的点积和范数
# - 底层用 HNSW 等索引算法，在千万级向量里找最近邻居也能毫秒完成
