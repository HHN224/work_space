# ============================================
# 补充课：invoke() vs from_messages() 到底啥区别？
# ============================================
# 
# 核心结论：
#   from_messages() = 写菜谱（定义模板）
#   invoke()        = 炒菜（执行/运行）
# 
# 它们根本不是竞争对手，而是搭档：
#   先用 from_messages() 写出菜谱 → 再用 invoke() 把菜炒出来
# ============================================

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

API_KEY = "sk-b521837677174c9bb4cbb86091187826"      # ← 改成你的真实 Key！
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-chat"

ai = ChatOpenAI(
    model=MODEL,
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.7,
)

print("=" * 50)
print("【比喻】把 LangChain 比作一家餐厅")
print("=" * 50)


# ============================================
# 1. from_messages() = 写菜谱（定义模板）
# ============================================
# 
# from_messages() 是 ChatPromptTemplate 的一个"构造函数"。
# 它的作用是：提前规定好"对话的格式"。
#
# 生活比喻：
#   你是餐厅老板，from_messages() 就是你在写"标准菜谱"：
#   - 第一行：厨师收到菜后要先说什么（system 角色）
#   - 第二行：顾客点了什么菜（human 角色）
#   - {dish} 表示"这道菜的名字待定，上菜时再填"
#
# 注意：这时候 AI 还没开始说话！你只是在"准备"。

print("\n=== 1. 用 from_messages() 写菜谱 ===")
print("（这时候只是定义，AI 还没运行）")

menu = ChatPromptTemplate.from_messages([
    ("system", "你是一位米其林三星主厨，对每道菜都能说出它的精髓。"),
    ("human", "请介绍一下{dish}这道菜")
])

print(f"✅ 菜谱写好了！它是一个 '模板对象'，还没有运行。")
print(f"   模板里的变量是：{menu.input_variables}")  # 显示 ['dish']


# ============================================
# 2. invoke() = 炒菜（执行/运行）
# ============================================
# 
# invoke() 的意思是："把原料放进去，让它运转起来！"
# 
# 它可以用在很多东西上：
#   - 用在 Prompt 模板上 → 把变量填进去，生成完整的对话
#   - 用在 AI 模型上 → 把对话发给 AI，得到回答
#   - 用在 Chain 上 → 从头到尾跑一遍流水线
#
# 生活比喻：
#   invoke() 就是 "开火炒菜" 这个动作。
#   但你要先知道：给谁开火？

print("\n=== 2. 用 invoke() 执行不同的东西 ===")


# ---- 2.1 给"菜谱" invoke：填空 ----
# 菜谱.invoke({"dish": "红烧肉"}) → 输出一份"填好空的完整菜单"
print("\n--- 2.1 给 Prompt 模板 invoke（填空）---")

filled_menu = menu.invoke({"dish": "红烧肉"})
print(f"输入：{{'dish': '红烧肉'}}")
print(f"输出：{filled_menu}")  # 你会看到里面包含 SystemMessage 和 HumanMessage
print("说明：只是把 {dish} 换成了 '红烧肉'，还没有问 AI！")


# ---- 2.2 给"AI" invoke：打电话 ----
# ai.invoke("问题") → 把问题发给 DeepSeek，得到回答
print("\n--- 2.2 给 AI 直接 invoke（打电话）---")
print("你问：'天为什么是蓝的？'")

answer = ai.invoke("天为什么是蓝的？")
print(f"AI 回答：{answer.content}")
print("说明：直接打电话问 AI，没有设定身份，就是闲聊。")


# ---- 2.3 给"AI" 传入填好的菜谱 invoke：带身份打电话 ----
# ai.invoke(filled_menu) → 把刚才填好的菜单发给 AI
print("\n--- 2.3 给 AI 传入填好的菜谱 invoke（带身份打电话）---")

# 先填空：{dish} → "佛跳墙"
filled_menu2 = menu.invoke({"dish": "佛跳墙"})
print("菜谱已填好：dish = 佛跳墙")

# 把填好的菜单传给 AI
answer2 = ai.invoke(filled_menu2)
print(f"AI 回答（以米其林主厨身份）：{answer2.content[:100]}...")
print("说明：AI 现在知道自己是米其林主厨了，回答会带上专业感。")


# ---- 2.4 给"Chain" invoke：全自动流水线 ----
# chain.invoke() = 填空 + 打电话 + 整理，一步完成
print("\n--- 2.4 给 Chain invoke（全自动）---")

parser = StrOutputParser()
chain = menu | ai | parser  # 菜谱 → AI → 整理器

print("流水线已组装：menu | ai | parser")
print("你只需说：我想了解 '扬州炒饭'")

final_result = chain.invoke({"dish": "扬州炒饭"})
print(f"最终结果：{final_result[:100]}...")
print("说明：你只说了一句话，流水线自动完成了：填空 → 问 AI → 整理文字")


# ============================================
# 总结对比表
# ============================================
print("\n" + "=" * 50)
print("【终极总结】")
print("=" * 50)
print("""
┌─────────────────┬────────────────────────┬────────────────────────┐
│     方法        │      作用（比喻）      │        使用对象         │
├─────────────────┼────────────────────────┼────────────────────────┤
│ from_messages() │   写菜谱（定义模板）   │   ChatPromptTemplate   │
│                 │   规定谁说什么话       │                        │
├─────────────────┼────────────────────────┼────────────────────────┤
│    invoke()     │   开火炒菜（执行）     │   Prompt / AI / Chain  │
│                 │   让它运转起来         │   几乎所有组件都能用   │
└─────────────────┴────────────────────────┴────────────────────────┘

invoke() 就像 "启动" 按钮：
  - 按在 Prompt 上 → 把变量填进去
  - 按在 AI 上 → 打电话问问题
  - 按在 Chain 上 → 跑完整条流水线

from_messages() 就像 "Word 文档模板"：
  - 你先写好一个带空格的模板
  - 运行时 invoke() 帮你把空格填满
""")
