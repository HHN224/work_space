import os
import math
import json
from datetime import datetime
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END


class OrchestratorState(TypedDict):
    task:           str           # 用户的原始请求
    research_notes: list[str]     # 研究员收集到的事实
    draft:          str           # 写手/总结员完成的文本
    next_agent:     str           # 主管的路由决策
    iterations:     int           # 安全计数器，防止无限循环
    final_output:   str           # 返回给用户的内容



llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.environ.get("DEEPSEEK_API_KEY", "sk-515871595dbc4087adc4ae873dd90426"),
    model="deepseek-chat",
    temperature=0.7,
)

def researcher(state: OrchestratorState) -> OrchestratorState:
    """收集与任务主题相关的事实信息。"""
    print("\n[研究员] 工作中...")

    response = llm.invoke([
        SystemMessage(content="你是一个研究员，负责收集与用户请求相关的事实信息。用 4-6 个简洁的要点回复。不要废话，不要下结论 —— 只陈述事实。"),
        HumanMessage(content=f"用户的请求是: {state['task']}")
    ])

    note = response.content.strip()
    print(f"  已收集研究 ({len(note)} 字符)")

    return {
        **state,
        "research_notes": state["research_notes"] + [note],
        "next_agent":     "supervisor"    # 总是把控制权交还给主管
    }


def summarizer(state: OrchestratorState) -> OrchestratorState:
    """通过分析研究员的笔记来生成洞察。"""
    print("\n[总结员] 工作中...")

    notes_text = "\n\n".join(state["research_notes"])

    response = llm.invoke([
        SystemMessage(content=(
            "你是一个分析专家。根据研究笔记，找出 3 个最重要的"
            "模式、权衡或影响。要精确且简洁。"
        )),
        HumanMessage(content=f"用户的请求是: {state['task']}\n\n研究笔记:\n{notes_text}\n\n请提供你的分析。")
    ])

    analysis = response.content.strip()
    print(f"  分析完成 ({len(analysis)} 字符)")

    return {
        **state,
        "draft": state["draft"] + "\n分析洞察:\n" + analysis,
        "next_agent": "supervisor"    # 总是把控制权交还给主管
    }


_SUPERVISOR_SYSTEM = (
    "你是一名工作流主管。负责编排一个 研究->总结 的流水线。\n"
    "可用智能体只有三个：researcher（研究员）、summarizer（总结员）、FINISH（完成）。\n\n"
    "严格遵循以下规则选择 next：\n"
    "1. 如果 research_notes 为空 -> 必须选 researcher\n"
    "2. 如果 research_notes 非空但 draft 为空 -> 必须选 summarizer\n"
    "3. 如果 draft 非空 -> 选 FINISH\n"
    "4. 永远不要跳过 summarizer 直接 FINISH\n\n"
    "只输出一个 JSON 对象，格式必须完全符合（不要用 markdown 代码块，不要额外文字）:\n"
    '{"next": "researcher|summarizer|FINISH", "reason": "简短解释"}'
)


def supervisor(state: OrchestratorState) -> OrchestratorState:
    """根据当前状态决定下一个智能体。"""
    print("\n[主管] 决策中...")

    status = (
        f"任务: {state['task']}\n\n"
        f"已完成研究轮数 : {len(state['research_notes'])}\n"
        f"草稿/分析已完成 : {'是' if state['draft'] else '否'}\n"
        f"已使用迭代次数 : {state['iterations']} / 5\n"
    )

    response = llm.invoke([
        SystemMessage(content=_SUPERVISOR_SYSTEM),
        HumanMessage(content=status)
    ])

    content = response.content.strip()

    try:
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        decision = json.loads(content)
        next_agent = decision.get("next", "FINISH")
        reason     = decision.get("reason", "")
    except Exception as e:
        print(f"  JSON 解析失败 ({e})，回退到 FINISH")
        next_agent = "FINISH"
        reason = "解析错误"

    print(f"  -> 下一步: {next_agent}  ({reason})")
    return {
        **state,
        "next_agent": next_agent,
        "iterations": state["iterations"] + 1
    }


def route_from_supervisor(state: OrchestratorState) -> str:
    """将主管的决策映射到下一个图节点。"""
    if state["iterations"] >= 5:
        print("  达到迭代上限 —— 强制结束")
        return "finish"
    decision = state["next_agent"]
    return decision if decision in ("researcher", "summarizer") else "finish"


def finish(state: OrchestratorState) -> OrchestratorState:
    """收集最终输出。"""
    print("\n[结束] 收尾中...")
    return {
        **state,
        "final_output": state["draft"] or "没有产生输出。"
    }


def build_orchestrator():
    graph = StateGraph(OrchestratorState)

    graph.add_node("supervisor", supervisor)
    graph.add_node("researcher", researcher)
    graph.add_node("summarizer", summarizer)
    graph.add_node("finish", finish)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "summarizer": "summarizer",
            "finish":     "finish"
        }
    )

    graph.add_edge("researcher", "supervisor")
    graph.add_edge("summarizer", "supervisor")

    graph.add_edge("finish", END)

    return graph.compile()



if __name__ == "__main__":
    agent = build_orchestrator()

    result = agent.invoke({
        "task":           "agent 是什么",
        "research_notes": [],
        "draft":          "",
        "next_agent":     "",
        "iterations":     0,
        "final_output":   ""
    })

    print("\n" + "=" * 60)
    print("最终结果:")
    print("=" * 60)
    print(result["final_output"])
