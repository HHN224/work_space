from pydantic import BaseModel, Field
from typing import List, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END, add_messages
import os 
import sys
from langchain_core.utils.function_calling import convert_to_openai_function

from langchain_openai import ChatOpenAI
# from langchain_community.chat_models.tongyi import ChatTongyi

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    BaseMessage,
)
from langchain.tools import tool
from langchain.callbacks import StdOutCallbackHandler


import json

@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的天气
    """
    return f"{city} 的天气是晴天。"

@tool
def get_time() -> str:
    """
    获取当前时间
    """
    from datetime import datetime
    return f"当前时间是 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}。"   

@tool 
def get_stockprice(ticker: str) -> str:
    """
    查询指定公司的股票价格
    """
    return f"{ticker} 的股价是 $100。"

tools = [
    get_weather,
    get_stockprice,
    get_time
]
tool_map = {tool.name: tool for tool in tools}

# ---- DeepSeek LLM 配置 ----
if not os.environ.get("DEEPSEEK_API_KEY"):
    print("错误: 未设置 DEEPSEEK_API_KEY 环境变量。")
    print("请在运行脚本前设置，例如:")
    print('  $env:DEEPSEEK_API_KEY="sk-xxx"   (PowerShell)')
    print('  export DEEPSEEK_API_KEY=sk-xxx    (Bash)')
    exit(1)

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    model="deepseek-chat",
    temperature=0.7,
).bind_tools(tools)

class GraphState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]
    tool_outputs: List[str] = Field(default_factory=list)
                       

def run_llm(state: GraphState) -> dict:
    response = llm.invoke(state.messages)
    return {"messages": response}

def check_tool_use_needed(state: GraphState) -> str:
    last = state.messages[-1]
    if last.tool_calls:
        return "call_tool"
    return "end"



def call_tool(state: GraphState) -> dict:
    last_message = state.messages[-1]
    tool_messages = [] 

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        print(f"正在执行工具: {tool_name}")

        if tool_name not in tool_map:
            raise ValueError(f"工具 {tool_name} 未找到。")
        
        selected_tool = tool_map[tool_name]
        
        result = selected_tool.run(tool_call["args"])
    
        tool_messages.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    
    return {"messages": tool_messages}



builder = StateGraph(GraphState)

builder.add_node("llm", run_llm)
builder.add_node("call_tool", call_tool)

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", check_tool_use_needed, {
    "call_tool": "call_tool",
    "end" : END
})

builder.add_edge("call_tool", "llm")
graph = builder.compile()



system_prompt = SystemMessage(content="你是一个有帮助的助手。在需要时使用工具。你会用像《哈利·波特》中斯内普教授一样的语气回答问题，并把用户当成哈利·波特。当你使用工具时，不需要使用这种语气。")
user_query = HumanMessage(content="杭州的天气怎么样？现在几点了？阿里巴巴的股价是多少？")

initial_state = GraphState(messages=[system_prompt, user_query])

final_state = graph.invoke(initial_state)  


print(final_state)
print("==="*10)
for msg in final_state["messages"]:
    if isinstance(msg, AIMessage) and msg.content != '':
        print(f"AI: {msg.content}")
