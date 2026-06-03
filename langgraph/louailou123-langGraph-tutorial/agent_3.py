from typing import TypedDict,List
from langgraph.graph import StateGraph,START,END

class third_agent_state(TypedDict):
    number1: int
    number2:int
    operation1:str
    number3:int
    number4:int
    operation2:str
    result1:int
    result2:int

def addition_node1(state:third_agent_state)->third_agent_state:
    state["result1"]=state["number1"]+state["number2"]
    return state

def substraction_node1(state:third_agent_state)->third_agent_state:
    state["result1"]=state["number1"]-state["number2"]
    return state
def router1 (state:third_agent_state)->str:
    if state["operation1"]=="+":
        return "addition_node1"
    else:
        return "substraction_node1"

def addition_node2(state:third_agent_state)->third_agent_state:
    state["result2"]=state["number3"]+state["number4"]
    return state

def substraction_node2(state:third_agent_state)->third_agent_state:
    state["result2"]=state["number3"]-state["number4"]
    return state
def router2 (state:third_agent_state)->str:
    if state["operation2"]=="+":
        return "addition_node2"
    else:
        return "substraction_node2"

graph=StateGraph(third_agent_state)

graph.add_node("addition_node1",addition_node1)
graph.add_node("substraction_node1",substraction_node1)
graph.add_node("addition_node2",addition_node2)
graph.add_node("substraction_node2",substraction_node2)
graph.add_node("router1",lambda state:state)
graph.add_node("router2",lambda state:state)

graph.add_edge(START,"router1")
graph.add_conditional_edges("router1",router1 , {
    "addition_node1":"addition_node1",
    "substraction_node1": "substraction_node1"
})

graph.add_edge("addition_node1","router2")
graph.add_edge("substraction_node1","router2")

graph.add_conditional_edges("router2",router2 , {
    "addition_node2":"addition_node2",
    "substraction_node2": "substraction_node2"
})

graph.add_edge("addition_node2",END)
graph.add_edge("substraction_node2",END)

app=graph.compile()

print(app.get_graph().print_ascii())

with open("agent_3_graph.png", "wb") as f:
    f.write(app.get_graph().draw_mermaid_png())

result=app.invoke({"number1":10,"number2":5,"operation1":"+","number3":20,"number4":10,"operation2":"-"})

print(result)
