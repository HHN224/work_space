# ============================================
# LangChain 第1课：零基础入门
# 目标：让 AI 开口说话，理解 3 个最基本概念
# ============================================
# 
# 在开始之前，只需要做一件事：
# 把你的 DeepSeek API Key 填到下面第 18 行。
# 
# 如果你不知道 API Key 在哪：
# 登录 https://platform.deepseek.com/ → 左侧"API keys" → 创建并复制
# ============================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ============================================
# 【配置区】把你的 API Key 填在这里
# ============================================
API_KEY = "sk-b521837677174c9bb4cbb86091187826"      # ← 改成你的真实 Key！
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"


# ============================================
# 步骤一：创建一个 "AI 对象"
# ============================================
# 
# 生活比喻：
# 想象你买了一部可以打给 AI 的电话。
# ChatOpenAI 就是这部 "电话机"，它负责把你的话传给 DeepSeek，再把回答传回来。
# 
# 为什么要用 ChatOpenAI，而不用 DeepSeek 官方的 SDK？
# 因为 DeepSeek 是 "兼容 OpenAI 格式" 的，所以 LangChain 用 ChatOpenAI 就能连上它。
# 这也是 LangChain 的强大之处——换模型几乎不用改代码。

print("=== 步骤一：创建 AI 对象 ===")

ai = ChatOpenAI(
    model=MODEL,           # 用哪个模型？
    api_key=API_KEY,       # 你的身份凭证
    base_url=BASE_URL,     # 服务器地址
    temperature=0.7,       # 温度：0=很严肃，1=很有创意
)

print("✅ AI 对象创建成功！这就像你拿起了一部电话。\n")


# ============================================
# 步骤二：直接和 AI 对话
# ============================================
# 
# 生活比喻：
# 你直接对着电话说："什么是 LangChain？"
# AI 回答你一段话。
# 
# 在代码里，"说话" 叫 .invoke()，"回答" 是一个对象，取 .content 就是文字。

print("=== 步骤二：直接对话 ===")
print("你问 AI：什么是 LangChain？")
print("AI 正在思考...")

response = ai.invoke("什么是 LangChain？")
print(f"AI 回答：{response.content}\n")


# ============================================
# 步骤三：给 AI 设定身份（Prompt Template）
# ============================================
# 
# 生活比喻：
# 你打电话时，对 AI 说："你现在是小学老师，用小学生能听懂的话解释什么是太阳。"
# AI 就会换一种语气、换一种难度来回答。
# 
# 在 LangChain 里，这叫 "Prompt Template"（提示词模板）。
# 模板里用 {topic} 这种花括号表示 "这里要填空"。

print("=== 步骤三：给 AI 设定身份 ===")

# 创建一个 "提示词模板"
# system: 给 AI 的"系统指令"（相当于你告诉它"你现在是谁"）
# human: 人类的提问（{topic} 是一个变量，会被替换成真实内容）
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一位幽默风趣的小学老师，总是用简单有趣的方式讲解知识。"),
    ("human", "请给我讲解一下：{topic}")
])

# 给模板 "填空"，{topic} 变成 "什么是区块链"
filled_prompt = prompt_template.invoke({"topic": "什么是区块链"})
print("你设定的身份：幽默的小学老师")
print("你提的问题：什么是区块链\n")

# 把填好的内容发给 AI
print("AI 正在用小学老师的口吻思考...")
response2 = ai.invoke(filled_prompt)
print(f"AI 回答：{response2.content}\n")


# ============================================
# 步骤四：把 "填空 + 打电话 + 听回答" 串成一条流水线
# ============================================
# 
# 生活比喻：
# 想象一个工厂流水线：
# 步骤1：把原材料放进模板（填空）
# 步骤2：把填好的内容传给 AI（打电话）
# 步骤3：把 AI 的回答整理成纯文字（去掉多余格式）
# 
# 在 LangChain 里，用 "|" 符号把步骤串起来，这叫做 "Chain"（链）。
# "|" 的意思就是 "左边做完，结果传给右边"。

print("=== 步骤四：串成一条 Chain（流水线）===")

# 输出解析器：把 AI 返回的复杂对象，变成纯字符串
parser = StrOutputParser()

# 用 "|" 把三个步骤串起来
# 输入 → prompt_template（填空）→ ai（问模型）→ parser（整理文字）
chain = prompt_template | ai | parser

# 现在只要一句话，流水线自动跑完！
print("你问：什么是量子计算机？")
print("流水线自动运行：填空 → 打电话 → 整理...")

result = chain.invoke({"topic": "什么是量子计算机"})
print(f"最终结果：{result}\n")


# ============================================
# 课后总结（务必读一下）
# ============================================
print("=== 本课总结 ===")
print("""
今天你只需要记住 3 个东西：

1. ChatOpenAI —— "电话机"
   负责连接 AI 模型（DeepSeek），把你说的话传过去，把回答传回来。

2. ChatPromptTemplate —— "带空格的问卷"
   提前写好一个 "格式"，运行时把变量（如 {topic}）填进去。
   好处是：同一个模板可以反复用，换内容就行。

3. Chain —— "流水线"
   用 "|" 把多个步骤串起来，数据从左流到右，自动处理。
   好处是：你想加步骤、换步骤，都很方便。

就像你学 Flask 时：
- 第1天跑通了 "Hello World"
- 第2天才理解 @app.route 是什么
- 第3天才学数据库

LangChain 也一样：先跑通，再慢慢理解。
""")
