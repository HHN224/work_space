"""
01 - 简单的状态图 (Simple State Graph)
======================================
学习 LangGraph 的 4 个核心概念：

  1. STATE（状态） —— 一个 TypedDict，在每个节点之间流动
  2. NODES（节点） —— 纯函数：接收 state，返回更新后的 state
  3. EDGES（边）   —— 节点之间的连接（固定边或条件边）
  4. END（结束）   —— 一个特殊的终止节点，用来停止执行

本示例的图结构：
  [START] → initialize → process → process → process → finalize → [END]
                               ↑_______________|  (当 step_count < 3 时循环)
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END


# ─────────────────────────────────────────────────────────────────────────────
# 1. STATE（状态）
# 每个节点都会收到这个字典，并返回一个（可选修改后的）副本。
# 你可以把它理解为 Agent 的"工作记忆"。
# ─────────────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: list[str]   # 记录发生了什么
    step_count: int       # 我们已经执行了多少步
    final_answer: str     # 最终答案，在最后一步填入


# ─────────────────────────────────────────────────────────────────────────────
# 2. NODES（节点）
# 每个节点就是一个函数：(state) -> (部分 state 更新)
# ─────────────────────────────────────────────────────────────────────────────

def initialize(state: AgentState) -> AgentState:
    """入口节点 —— 设置初始值。"""
    print("[节点] initialize")
    return {
        **state,
        "step_count": 0,
        "messages": ["开始任务..."]
    }


def process(state: AgentState) -> AgentState:
    """工作节点 —— 执行一个工作单元，然后由路由决定是否需要循环。"""
    step = state["step_count"] + 1
    print(f"[节点] process  (第 {step}/3 步)")
    return {
        **state,
        "step_count": step,
        "messages": state["messages"] + [f"完成第 {step} 步"]
    }


def finalize(state: AgentState) -> AgentState:
    """终止节点 —— 汇总结果。"""
    print("[节点] finalize")
    summary = " → ".join(state["messages"])
    return {
        **state,
        "final_answer": f"共执行 {state['step_count']} 步后完成: [{summary}]"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. 路由函数
# 返回下一个节点的名字（字符串）。
# 这就是条件分支 / 循环的实现方式。
# ─────────────────────────────────────────────────────────────────────────────

def route_after_process(state: AgentState) -> str:
    """决定：继续循环回 'process'，还是前进到 'finalize'。"""
    if state["step_count"] < 3:
        return "process"    # 继续循环
    return "finalize"       # 完成，前进


# ─────────────────────────────────────────────────────────────────────────────
# 4. 构建图
# ─────────────────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    # 注册节点
    graph.add_node("initialize", initialize)
    graph.add_node("process",    process)
    graph.add_node("finalize",   finalize)

    # 设置执行起点
    graph.set_entry_point("initialize")

    # 固定边：initialize 总是指向 process
    graph.add_edge("initialize", "process")

    # 条件边：process 之后，调用 route_after_process() 来决定下一步
    graph.add_conditional_edges(
        "process",              # 源节点
        route_after_process,    # 路由函数
        {
            "process":  "process",   # 返回值 → 目标节点
            "finalize": "finalize",
        }
    )

    # 固定边：finalize 指向内置的 END 终止符
    graph.add_edge("finalize", END)

    return graph.compile()


# ─────────────────────────────────────────────────────────────────────────────
# 运行
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  示例 1 —— 简单的状态图（不涉及 LLM 调用）")
    print("=" * 55)

    app = build_graph()

    # 用初始状态调用图
    result = app.invoke({
        "messages":     [],
        "step_count":   0,
        "final_answer": ""
    })

    print("\n[结果] 最终状态:")
    print(f"  步数      : {result['step_count']}")
    print(f"  消息记录   : {result['messages']}")
    print(f"  最终答案   : {result['final_answer']}")
    print()
    print("关键要点:")
    print("  · State 流经每个节点，除非节点更新它，否则保持不变")
    print("  · add_conditional_edges() 是实现循环和分支的方式")
    print("  · END 停止图的执行 —— 没有它，执行永远不会终止")
