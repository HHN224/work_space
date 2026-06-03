# ============================================
# LangChain 第2课：Prompt 工程化
# 目标：学会让 AI 按照你想要的方式回答
# ============================================
# 
# 新知识点：
#   1. 多变量模板 + 默认值
#   2. Few-shot（给 AI 看例子，让它模仿）
#   3. 条件选择（不同场景换不同 Prompt）
#
# 💰 省钱模式：
#   把下面第 19 行的 MOCK_MODE 改成 True，程序不会调用 API，
#   直接打印"模拟回答"。你可以先跑逻辑，确认懂了再改 False 看真效果。
# ============================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ============================================
# 【配置区】
# ============================================
API_KEY = "sk-b521837677174c9bb4cbb86091187826"      # ← 改成你的真实 Key！
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

MOCK_MODE = False                    # ← True=模拟模式（不花钱），False=真调用 API


# ============================================
# 初始化 AI（如果 MOCK_MODE=True，这个其实不会用到，但先创建也没事）
# ============================================
ai = ChatOpenAI(
    model=MODEL,
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.5,                  # 0.5 比较适中，既不太死板也不太放飞
)

parser = StrOutputParser()


def mock_or_invoke(chain, input_data, description):
    """
    一个小辅助函数：
    如果 MOCK_MODE=True，就假装 AI 回答了，不花钱。
    如果 MOCK_MODE=False，就真调用 API。
    """
    print(f"\n【运行】{description}")
    print(f"输入数据：{input_data}")
    
    if MOCK_MODE:
        print("🟡 模拟模式：这里会调用 API，但现在用假数据代替")
        # 模拟一个符合场景的回答
        if "温柔" in str(input_data):
            print("AI 回答（模拟）：亲爱的，没关系的，一切都会好起来的~ 🌸")
        elif "暴躁" in str(input_data):
            print("AI 回答（模拟）：这么简单的问题你都不会？！给我认真听好了！💢")
        elif "few_shot" in str(input_data) or "正式" in str(input_data):
            print("AI 回答（模拟）：根据您提供的范例，我已将内容转换为正式表述。")
        else:
            print("AI 回答（模拟）：这是一个模拟的回答内容。")
        print("（把 MOCK_MODE 改成 False，并填入真 Key，就能看到 AI 的实时回答了）")
    else:
        print("🟢 正在调用 DeepSeek API...")
        result = chain.invoke(input_data)
        print(f"AI 回答：{result}")


# ============================================
# 步骤一：多变量 Prompt 模板
# ============================================
# 
# 生活比喻：
#   第一课只填一个空：{topic}
#   现在我们要填多个空：{style}、{content}、{length}
#   就像做一份详细的问卷调查，有很多选项。

print("=" * 50)
print("步骤一：多变量 Prompt 模板")
print("=" * 50)

multi_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位{style}风格的写作助手。"),
    ("human", "请用不超过{length}字，介绍一下：{content}")
])

# 把变量填进去：style=幽默、length=50、content=Python
data = {
    "style": "幽默",
    "length": "50",
    "content": "Python 这门编程语言"
}

# 看看填完后的效果（不调用 AI，只是展示"卷子填好了"的样子）
filled = multi_prompt.invoke(data)
print("\n【Prompt 模板填空后的内部结构】")
print(filled)


# ============================================
# 步骤二：Few-shot（给 AI 看例子，让它模仿）
# ============================================
# 
# 生活比喻：
#   你想教一个小学生做"把口语改成书面语"的作业。
#   你光说"改成书面语"，他可能改不好。
#   但如果你先给他看 3 个例题：
#     "挺好的" → "效果良好"
#     "挺多的" → "数量庞大"
#     "挺快的" → "速度优异"
#   他看了例子后，就明白规律了，后面的题也会做了。
#
# 这就是 Few-shot Learning：给 AI 看几个 "输入 → 输出" 的例子，
# 它就能抓住规律，应用到新问题上。

print("\n" + "=" * 50)
print("步骤二：Few-shot（少样本学习）")
print("=" * 50)

# 定义几个 "例题"
examples = [
    {"input": "这个产品挺好的", "output": "该产品性能表现优异，质量可靠。"},
    {"input": "用户挺多的",   "output": "该产品拥有庞大的用户基础。"},
    {"input": "加载挺快的",   "output": "系统响应速度迅速，加载体验流畅。"},
]

# 创建"例题模板"：规定例子的格式
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}")
])

# 把例题模板和具体例题组合起来
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,   # 用哪个格式展示例子
    examples=examples,               # 具体的例题列表
)

# 组装完整 Prompt：
# system + 例题(few_shot) + 新的问题(human)
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位专业的公文写作助手。你的任务是把口语化的表达转换成正式的书面语。请参考下面的例子，以相同的风格改写用户的新句子。"),
    few_shot_prompt,  # ← 这就是例题区！
    ("human", "{input}"),
])

chain_fewshot = final_prompt | ai | parser

mock_or_invoke(chain_fewshot, {"input": "这个按钮按下去反应挺灵敏的"}, "Few-shot 改写句子")


# ============================================
# 步骤三：条件选择——不同场景用不同 Prompt
# ============================================
# 
# 生活比喻：
#   你去一家餐厅，服务员问你："您想要什么风格的服务？"
#   A. 温柔模式 → 轻声细语
#   B. 暴躁模式 → 直来直去
#   C. 学术模式 → 严谨专业
#   你选了 A，服务员就按 A 的风格来接待你。
#
# 在代码里，我们可以定义好几个 Prompt，根据用户的选择来"加载"对应的那个。

print("\n" + "=" * 50)
print("步骤三：条件选择——选择你的 AI 性格")
print("=" * 50)

# 定义三种性格的 Prompt
templates = {
    "温柔": ChatPromptTemplate.from_messages([
        ("system", "你是一位温柔体贴的心理咨询师，说话轻声细语，总是先肯定对方的感受。"),
        ("human", "{question}")
    ]),
    "暴躁": ChatPromptTemplate.from_messages([
        ("system", "你是一位严厉的老师，说话直截了当，不留情面，但都是为了对方好。"),
        ("human", "{question}")
    ]),
    "学术": ChatPromptTemplate.from_messages([
        ("system", "你是一位严谨的研究员，说话必须引用概念，逻辑清晰，分点论述。"),
        ("human", "{question}")
    ]),
}

def get_ai_chain(style: str):
    """
    根据用户选择的风格，返回对应的 Chain。
    这就是最简单的"路由"——根据条件选择组件。
    """
    if style not in templates:
        print(f"⚠️ 不认识风格 '{style}'，默认用温柔模式")
        style = "温柔"
    
    prompt = templates[style]
    return prompt | ai | parser


# 测试：同一个问题，用三种性格各问一次
question = "我总是拖延任务，该怎么办？"

for style in ["温柔", "暴躁", "学术"]:
    print(f"\n--- 切换至【{style}模式】---")
    chain = get_ai_chain(style)
    mock_or_invoke(chain, {"question": question}, f"{style}模式回答问题")


# ============================================
# 课后总结
# ============================================
print("\n" + "=" * 50)
print("【第二课总结】")
print("=" * 50)
print("""
今天你学会了 Prompt 工程的 3 个武器：

1. 多变量模板
   {style}、{length}、{content}...
   就像一个问卷调查，你填什么，AI 就按什么条件回答。

2. Few-shot（给例子）
   AI 其实很笨，抽象指令它听不懂。
   但如果你给它看 3 个 "输入→输出" 的例子，它马上就能模仿。
   这是提升 AI 质量的**最强技巧之一**。

3. 条件选择
   把不同的 Prompt 存进字典（templates），根据用户选择来加载。
   这是做"多角色 AI"、"多场景 AI" 的基础。

🧠 思考：你现在能把第1课的 Chain，和第2课的 Prompt 工程，组合起来了吗？
   输入 {"style":"温柔", "question":"..."} → Chain 自动选择温柔模板 → 问 AI → 输出。
   这就是你的第一个"智能应用"的雏形！

下一步（第3课）：我们将学习如何让 AI 读你的文档，然后基于文档内容回答——这就是 RAG！
""")
