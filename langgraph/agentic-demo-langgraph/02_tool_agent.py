"""
02 - ReAct 工具智能体 (ReAct Tool Agent)
=========================================
ReAct = Reason（推理）+ Act（行动）。智能体的流程：
  1. 向 DeepSeek 发送问题（附带工具定义）
  2. LLM 要么直接回答，要么请求调用工具
  3. 我们执行工具并把结果返回给 LLM
  4. 重复直到 LLM 不再请求工具

图的形状：
  [START] -> call_llm -> execute_tools -> call_llm -> ... -> [END]
                   v (没有工具调用时)
                 [END]

本示例中的工具：
  * calculator   —— 安全的数学表达式求值
  * web_search   —— 模拟搜索（不涉及真实 HTTP）
  * get_time     —— 获取当前日期和时间
"""

import os
import math
import json
from datetime import datetime
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# ---------------------------------------------------------------------------
# DeepSeek LLM 配置
# ---------------------------------------------------------------------------

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
)

# ---------------------------------------------------------------------------
# STATE（状态）
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    question:     str
    messages:     list       # 完整的对话记录（LangChain 消息对象）
    tool_calls:   list       # 本轮 LLM 返回的 tool_call 列表
    final_answer: str        # LLM 的最后文本回复

# ---------------------------------------------------------------------------
# TOOL DEFINITIONS（工具定义）
# ---------------------------------------------------------------------------

_SEARCH_DB = {
    "python":     "Python 是一种高级动态类型语言，由 Guido van Rossum 于 1991 年创建。以可读性强和生态丰富著称。",
    "langgraph":  "LangGraph 是一个用于构建有状态、多角色 LLM 应用的库。它将工作流建模为图，节点是函数，边是流转。",
    "anthropic":  "Anthropic 是一家成立于 2021 年的 AI 安全公司。它创建了 Claude 系列模型，专注于安全和可操控的 AI。",
    "agentic ai": "Agentic AI 指的是 LLM 自主决定采取哪些行动（工具调用、子任务）来完成目标的系统，而不是只回复一次。",
}

@tool
def calculator(expression: str) -> str:
    """计算数学表达式。支持 +、-、*、/、** 以及 sqrt、sin、log 等函数。"""
    try:
        safe_builtins = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, safe_builtins)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算表达式时出错: {e}"

@tool
def web_search(query: str) -> str:
    """搜索某个主题的事实信息。返回一段简短的摘要。"""
    query_lower = query.lower()
    for keyword, info in _SEARCH_DB.items():
        if keyword in query_lower:
            return info
    return f"未找到 '{query}' 的具体数据。（这是一个演示，知识库很小。）"

@tool
def get_time() -> str:
    """返回当前的日期和时间。"""
    return f"当前日期/时间: {datetime.now().strftime('%A, %B %d %Y  %H:%M:%S')}"

tools = [calculator, web_search, get_time]
tool_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

# ---------------------------------------------------------------------------
# NODES（节点）
# ---------------------------------------------------------------------------

def call_llm(state: AgentState) -> AgentState:
    """
    把完整的对话历史发给 LLM。
    LLM 要么：
      (a) 返回文本答案  -> 我们完成了
      (b) 请求调用工具  -> 我们需要执行工具并循环回来
    """
    print("\n[LLM] 正在调用模型...")

    response = llm_with_tools.invoke(state["messages"])

    if response.content:
        print(f"  文本: {response.content[:80]}...")
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"  请求工具: {tc['name']}({json.dumps(tc['args'])})")

    return {
        **state,
        "messages":     state["messages"] + [response],
        "tool_calls":   response.tool_calls if response.tool_calls else [],
        "final_answer": response.content if not response.tool_calls else ""
    }


def execute_tools(state: AgentState) -> AgentState:
    """
    运行 LLM 请求的所有工具，并将结果打包成 ToolMessages。
    这些消息会被追加到对话历史中，以便 LLM 在下一轮看到。
    """
    print("\n[工具] 正在执行...")

    tool_messages = []
    for call in state["tool_calls"]:
        name = call["name"]
        args = call["args"]
        tool_call_id = call["id"]
        result = tool_map[name].invoke(args)
        print(f"  {name} -> {result}")
        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call_id))

    return {
        **state,
        "messages":   state["messages"] + tool_messages,
        "tool_calls": []       # 清空，防止路由意外循环
    }


# ---------------------------------------------------------------------------
# ROUTING（路由）
# ---------------------------------------------------------------------------

def route_after_llm(state: AgentState) -> str:
    """如果 LLM 请求了工具，就执行；否则结束。"""
    return "execute_tools" if state["tool_calls"] else END


# ---------------------------------------------------------------------------
# BUILD GRAPH（构建图）
# ---------------------------------------------------------------------------

def build_tool_agent():
    graph = StateGraph(AgentState)

    graph.add_node("call_llm",      call_llm)
    graph.add_node("execute_tools", execute_tools)

    graph.set_entry_point("call_llm")

    # LLM 之后：要么执行工具，要么停止
    graph.add_conditional_edges(
        "call_llm",
        route_after_llm,
        {"execute_tools": "execute_tools", END: END}
    )

    # 工具之后：总是回到 LLM（携带结果）
    graph.add_edge("execute_tools", "call_llm")

    return graph.compile()


# ---------------------------------------------------------------------------
# RUN（运行）
# ---------------------------------------------------------------------------

DEMO_QUESTIONS = [
    "840 的 15% 是多少？",
    "现在几点了？2 的 16 次方是多少？",
    "搜索一下 LangGraph 的相关信息，给我一个总结。",
]

if __name__ == "__main__":
    agent = build_tool_agent()

    for question in DEMO_QUESTIONS:
        print("\n" + "=" * 60)
        print(f"问题: {question}")
        print("=" * 60)

        result = agent.invoke({
            "question":     question,
            "messages":     [
                SystemMessage(content="你是一个有帮助的助手，可以使用工具。只要工具能帮助你给出更准确的答案，就使用它们。"),
                HumanMessage(content=question)
            ],
            "tool_calls":   [],
            "final_answer": ""
        })

        print(f"\n答案:\n{result['final_answer']}")

    print()
    print("关键要点:")
    print("  · 工具定义告诉 LLM 有哪些可用 —— LLM 自己决定什么时候用")
    print("  · 工具结果必须作为 ToolMessage 返回，并带上匹配的 tool_call_id")
    print("  · 循环会持续，直到 LLM 返回不带工具调用的文本答案")
