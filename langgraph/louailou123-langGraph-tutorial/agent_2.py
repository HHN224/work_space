from typing import TypedDict,List
from langgraph.graph import StateGraph


class second_agent_state(TypedDict):
    name:str
    values:List[int]
    operation:str
    result:str

def second_node(state:second_agent_state)->second_agent_state:
    ''' 这个节点会根据 operation 对 values 进行计算，并把结果写入 result '''
    if state["operation"] == "+":
        state["result"] = f"嗨 {state['name']}，你的答案是 {sum(state['values'])}"
    elif state["operation"] == "*":
        result=1
        for value in state["values"]:
            result *= value
        state["result"] = f"嗨 {state['name']}，你的答案是 {result}"
    else:
        state["result"] = f"嗨 {state['name']}，你的答案是 {None}"

    return state

graph=StateGraph(second_agent_state)

graph.add_node("second_node",second_node)

graph.set_entry_point("second_node")

graph.set_finish_point("second_node")

app=graph.compile()

result=app.invoke({"name":"bob","values":[1,2,10,5],"operation":"+"})

print(result["result"])
