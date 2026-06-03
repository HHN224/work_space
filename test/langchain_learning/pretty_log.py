# ============================================
# 辅助工具：打印消息历史，层级清晰，暴露全部细节
# ============================================
# 使用方法：
#   from pretty_log import print_messages
#   print_messages(messages)
# ============================================

import json
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


def print_messages(messages, title="对话历史"):
    """
    美观地打印 LangChain 消息列表，工具调用细节完全暴露。
    """
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")

    for i, msg in enumerate(messages, 1):
        role_icon = "📄"
        role_name = type(msg).__name__
        extra = ""

        if isinstance(msg, HumanMessage):
            role_icon = "🧑"
            role_name = "HumanMessage (用户)"

        elif isinstance(msg, AIMessage):
            role_icon = "🤖"
            role_name = "AIMessage (AI)"
            # tool_calls 原始 dict 完整打印
            if msg.tool_calls:
                extra_lines = []
                for tc in msg.tool_calls:
                    extra_lines.append(f"      tool_call: {json.dumps(tc, ensure_ascii=False)}")
                extra = "\n" + "\n".join(extra_lines)

        elif isinstance(msg, ToolMessage):
            role_icon = "🔧"
            role_name = "ToolMessage (工具返回)"
            extra = f"\n      tool_call_id: {msg.tool_call_id}"

        content = msg.content if msg.content else "(空)"
        print(f"[{i}] {role_icon} {role_name}")
        print(f"      content: {content}{extra}")

    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    demo_messages = [
        HumanMessage(content="15 的平方加上 23 是多少？"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculator",
                    "args": {"expression": "15**2 + 23"},
                    "id": "call_abc123xyz789",
                    "type": "tool_call"
                }
            ]
        ),
        ToolMessage(content="248", tool_call_id="call_abc123xyz789"),
        AIMessage(content="15 的平方是 225，加上 23 等于 248。"),
    ]

    print_messages(demo_messages, "演示：完整工具调用细节")
