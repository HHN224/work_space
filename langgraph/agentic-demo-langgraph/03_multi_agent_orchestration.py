"""
03 - 多智能体编排（主管模式）
=============================
真实的 Agentic 系统会把工作拆分给多个专业智能体。
本示例实现了 SUPERVISOR（主管）模式：

  +---------------------------------------------------------------+
  |                         主管 (SUPERVISOR)                       |
  |  （根据当前状态决定下一步调用哪个智能体）                         |
  +-------------+-------------------------------------------------+
                | 路由到...
        +-------+--------+------------------+
        v                v                  v
   [研究员]         [分析师]           [写手]
   收集事实         发现洞察          撰写输出
        |                |                  |
        +-------+--------+-- ---------------+
                v
          回到主管
                |
          完成 -> [END]

为什么用这个模式？
  · 每个智能体有明确的角色和独立的系统提示词
  · 主管拥有全局视角，智能地进行路由
  · 新增智能体时不需要改动主管的路由逻辑
"""

import os
import json
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# ---------------------------------------------------------------------------
# DeepSeek LLM 配置
# ---------------------------------------------------------------------------



llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key="sk-515871595dbc4087adc4ae873dd90426",
    model="deepseek-chat",
    temperature=0.7,
)

# ---------------------------------------------------------------------------
# STATE（状态，所有智能体共享）
# ---------------------------------------------------------------------------

class OrchestratorState(TypedDict):
    task:           str           # 用户的原始请求
    research_notes: list[str]     # 研究员收集到的事实
    analysis:       str           # 分析师的洞察
    draft:          str           # 写手完成的文本
    next_agent:     str           # 主管的路由决策
    iterations:     int           # 安全计数器，防止无限循环
    final_output:   str           # 返回给用户的内容


# ---------------------------------------------------------------------------
# 工作智能体 (WORKER AGENTS)
# 每个都是独立的 LLM 调用，有自己聚焦的系统提示词。
# 它们从状态中读取信息，完成工作，并将更新写回状态。
# ---------------------------------------------------------------------------


def researcher(state: OrchestratorState) -> OrchestratorState:
    """收集与任务主题相关的事实信息。"""
    print("\n[研究员] 工作中...")

    response = llm.invoke([
        SystemMessage(content=(
            "你是一名研究专家。你的唯一职责是收集关键事实。"
            "用 4-6 个简洁的要点回复。不要废话，不要下结论 —— 只陈述事实。"
        )),
        HumanMessage(content=f"收集关于以下主题的关键事实: {state['task']}")
    ])

    notes = response.content
    print(f"  已收集研究 ({len(notes)} 字符)")

    return {
        **state,
        "research_notes": state["research_notes"] + [notes],
        "next_agent":     "supervisor"    # 总是把控制权交还给主管
    }


def analyst(state: OrchestratorState) -> OrchestratorState:
    """从研究笔记中发现模式和洞察。"""
    print("\n[分析师] 工作中...")

    context = "\n\n---\n\n".join(state["research_notes"])

    response = llm.invoke([
        SystemMessage(content=(
            "你是一名分析专家。根据研究笔记，找出 3 个最重要的"
            "模式、权衡或影响。要精确且简洁。"
        )),
        HumanMessage(content=f"任务: {state['task']}\n\n研究笔记:\n{context}\n\n请提供你的分析。")
    ])

    analysis = response.content
    print(f"  分析完成 ({len(analysis)} 字符)")

    return {
        **state,
        "analysis":   analysis,
        "next_agent": "supervisor"
    }


def writer(state: OrchestratorState) -> OrchestratorState:
    """将研究 + 分析综合成一篇精炼的最终回复。"""
    print("\n[写手] 工作中...")

    notes_text = "\n\n".join(state["research_notes"])

    response = llm.invoke([
        SystemMessage(content=(
            "你是一名熟练的技术写手。将提供的研究和分析"
            "综合成一篇清晰、结构良好且引人入胜的回复。"
        )),
        HumanMessage(content=(
            f"任务: {state['task']}\n\n"
            f"研究笔记:\n{notes_text}\n\n"
            f"分析:\n{state['analysis']}\n\n"
            "写出一篇完整、精炼的回复。"
        ))
    ])

    draft = response.content
    print(f"  草稿完成 ({len(draft)} 字符)")

    return {
        **state,
        "draft":      draft,
        "next_agent": "supervisor"
    }


# ---------------------------------------------------------------------------
# 主管 (SUPERVISOR)
# 让 LLM 输出 JSON 格式的路由决策。
# 这样可以避免依赖本地模型服务器对 tool_choice 的支持。
# ---------------------------------------------------------------------------

_SUPERVISOR_SYSTEM = (
    "你是一名工作流主管。负责编排一个 研究->分析->写作 的流水线。\n"
    "典型顺序：先研究员，再分析师（需要先有研究），"
    "然后写手（需要研究和分析两者），最后完成 (FINISH)。"
    "不要重复已经产出输出的步骤。\n\n"
    "只输出一个 JSON 对象，格式必须完全符合（不要用 markdown 代码块，不要额外文字）:\n"
    '{"next": "researcher|analyst|writer|FINISH", "reason": "简短解释"}'
)


def supervisor(state: OrchestratorState) -> OrchestratorState:
    """
    读取当前状态并决定下一步调用哪个智能体。
    使用 LLM 的纯 JSON 输出，以获得最大的本地模型兼容性。
    """
    print("\n[主管] 决策中...")

    status = (
        f"任务: {state['task']}\n\n"
        f"已完成研究轮数 : {len(state['research_notes'])}\n"
        f"分析已完成     : {'是' if state['analysis'] else '否'}\n"
        f"草稿已完成     : {'是' if state['draft']    else '否'}\n"
        f"已使用迭代次数 : {state['iterations']} / 5\n"
    )

    response = llm.invoke([
        SystemMessage(content=_SUPERVISOR_SYSTEM),
        HumanMessage(content=status)
    ])

    content = response.content.strip()

    # 尝试解析 JSON 决策
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


# ---------------------------------------------------------------------------
# 路由 + 结束
# ---------------------------------------------------------------------------

def route_from_supervisor(state: OrchestratorState) -> str:
    """将主管的决策映射到下一个图节点。"""
    if state["iterations"] >= 5:
        print("  达到迭代上限 —— 强制结束")
        return "finish"
    decision = state["next_agent"]
    return decision if decision in ("researcher", "analyst", "writer") else "finish"


def finish(state: OrchestratorState) -> OrchestratorState:
    """收集最终输出。"""
    print("\n[结束] 收尾中...")
    return {
        **state,
        "final_output": state["draft"] or "没有产生输出。"
    }


# ---------------------------------------------------------------------------
# 构建图
# ---------------------------------------------------------------------------

def build_orchestrator():
    graph = StateGraph(OrchestratorState)

    graph.add_node("supervisor",  supervisor)
    graph.add_node("researcher",  researcher)
    graph.add_node("analyst",     analyst)
    graph.add_node("writer",      writer)
    graph.add_node("finish",      finish)

    # 主管是入口点
    graph.set_entry_point("supervisor")

    # 主管路由到某个工作智能体或结束
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "analyst":    "analyst",
            "writer":     "writer",
            "finish":     "finish"
        }
    )

    # 所有工作智能体都把控制权交回主管
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("analyst",    "supervisor")
    graph.add_edge("writer",     "supervisor")

    # 结束是唯一通往 END 的路径
    graph.add_edge("finish", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# 运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    task = "解释什么是 Agentic AI，以及为什么多智能体系统很有用"

    print("=" * 65)
    print("  示例 3 —— 多智能体编排（主管模式）")
    print(f"  任务: {task}")
    print("=" * 65)

    orchestrator = build_orchestrator()

    result = orchestrator.invoke({
        "task":           task,
        "research_notes": [],
        "analysis":       "",
        "draft":          "",
        "next_agent":     "",
        "iterations":     0,
        "final_output":   ""
    })

    print("\n" + "=" * 65)
    print("  最终输出")
    print("=" * 65)
    print(result["final_output"])

    print()
    print("关键要点:")
    print("  · 每个智能体只有一个聚焦的职责 —— 易于独立测试和改进")
    print("  · 主管本身不做工作 —— 它只负责路由")
    print("  · 主管使用 JSON 输出进行路由（与本地模型兼容性最高）")
    print("  · 迭代计数器是防止无限循环的安全阀")
