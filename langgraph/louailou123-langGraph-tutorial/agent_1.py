from typing import TypedDict
from langgraph.graph import StateGraph

class first_agent_state(TypedDict):
    name : str

def first_node(state : first_agent_state)->first_agent_state:
    ''' 这个节点会在 name 状态上追加一段字符串 '''
    
    state["name"] = state["name"] + "，你在学习 LangGraph 方面做得非常棒"
    return state


graph=StateGraph(first_agent_state)

graph.add_node("first_node",first_node)

graph.set_entry_point("first_node")

graph.set_finish_point("first_node")

app=graph.compile()

result=app.invoke({"name" : "bob"})

print(result["name"])
    
     
