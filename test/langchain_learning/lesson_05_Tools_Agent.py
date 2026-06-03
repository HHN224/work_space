# ============================================
# LangChain 第5课：Tools & Agent
# ============================================

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from pretty_log import print_messages

API_KEY = "sk-b521837677174c9bb4cbb86091187826"
BASE_URL = "https://api.deepseek.com/v1"

llm = ChatOpenAI(model="deepseek-chat", api_key=API_KEY, base_url=BASE_URL, temperature=0.1)

@tool
def calculator(expression: str) -> str:
    """用于计算数学表达式。传入字符串形式的数学表达式，如"15**2 + 23"，返回计算结果。"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算出错: {e}"

@tool
def get_today_weather(location: str) -> str:
    """用于获取指定地点当前天气。传入字符串形式的地点，如"广东"，返回当前地区天气的字符串。"""
    return f"{location}的天气为晴天"

llm_with_tools = llm.bind_tools([calculator, get_today_weather])

# --------------------------------------------
# 运行演示
# --------------------------------------------
question = "今天广东天气怎么样"
messages = [HumanMessage(content=question)]

print(f"【用户问题】{question}\n")

# 第1轮：AI 决定调用工具
ai_response = llm_with_tools.invoke(messages)
messages.append(ai_response)
print_messages(messages, "第1轮：AI 请求工具调用")

# 执行工具
for tool_call in ai_response.tool_calls:
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_id = tool_call["id"]

    tools_map = {"calculator": calculator, "get_today_weather": get_today_weather}
    tool = tools_map.get(tool_name)
    if tool:
        observation = tool.func(**tool_args)
    else:
        observation = "未知工具"

    messages.append(ToolMessage(content=observation, tool_call_id=tool_id))

print_messages(messages, "工具执行后")

# 第2轮：AI 根据工具结果生成最终回答
final_response = llm_with_tools.invoke(messages)
messages.append(final_response)
print_messages(messages, "最终：AI 给出完整回答")

print(f"\n🎯 最终答案：{final_response.content}")
