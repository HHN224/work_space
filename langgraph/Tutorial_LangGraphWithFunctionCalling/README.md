# LangGraph Agent with Function Calling

[中文版本 / Chinese Version](README_zh.md)

A conversational AI agent built with LangGraph that demonstrates function calling capabilities using Alibaba's Qwen language model. The agent can execute various tools while maintaining a conversational flow.

## Features

- **Function Calling**: Seamlessly integrates external tools with conversational AI
- **Multiple Tools**: Weather checking, time retrieval, and stock price queries
- **State Management**: Uses LangGraph's StateGraph for robust conversation flow
- **Conditional Logic**: Intelligent routing between conversation and tool execution
- **Personality Mode**: Optional Professor Snape persona for entertaining interactions
- **Qwen Integration**: Powered by Alibaba's Qwen-Plus model via ChatTongyi

## Architecture

The agent follows a graph-based architecture with two main nodes:

<div align="center">
  <img src="agent_function_calling.png" alt="Agent Function Calling Architecture" width="800"/>
</div>

### Components

1. **GraphState**: Pydantic model managing conversation state and tool outputs
2. **Tools**: Three built-in tools for weather, time, and stock price
3. **LLM Node**: Handles conversation and decides when to use tools
4. **Tool Node**: Executes selected tools and formats responses
5. **Conditional Router**: Determines whether tool execution is needed

## Available Tools

### Weather Tool
```python
@tool
def get_weather(city: str) -> str:
    """A tool to get the weather in a given city"""
```

### Time Tool
```python
@tool
def get_time() -> str:
    """A tool to get the current time"""
```

### Stock Price Tool
```python
@tool
def get_stockprice(ticker: str) -> str:
    """A tool to get the stock price of a given company ticker"""
```

## Prerequisites

- Python 3.8+
- Alibaba Cloud DashScope API access
- Required environment variables set up

## Installation

1. Install required dependencies:
```bash
pip install langgraph langchain-community pydantic
```

2. Set up environment variables:
```bash
export ALI_API_KEY="your_dashscope_api_key"
export ALI_BASE_URL="https://dashscope.aliyuncs.com/api/v1"  # optional
```

## Usage

### Basic Usage

```python
from test_langgraph import graph, GraphState
from langchain_core.messages import HumanMessage, SystemMessage

# Create initial state
system_prompt = SystemMessage(content="You are a helpful assistant.")
user_query = HumanMessage(content="What's the weather in Beijing?")
initial_state = GraphState(messages=[system_prompt, user_query])

# Run the agent
final_state = graph.invoke(initial_state)

# Display results
for msg in final_state["messages"]:
    if isinstance(msg, AIMessage) and msg.content:
        print(f"AI: {msg.content}")
```

### Example Interactions

**Multi-tool Query:**
```
User: "What is the weather in Hangzhou? What time is it? What is the stock price of ALIBABA?"

Agent: 
1. Executes get_weather("Hangzhou")
2. Executes get_time()
3. Executes get_stockprice("ALIBABA")
4. Provides comprehensive response with all information
```

**Professor Snape Mode:**
```python
system_prompt = SystemMessage(content="""
You are a helpful assistant. Use tools when needed. 
You will answer questions with tone like Prof. Snape in Harry Potter, 
and act like I am Harry Potter. When you use tools, you don't use such tone.
""")
```

## Configuration

### Model Configuration
```python
llm = ChatTongyi(
    dashscope_api_key=API_KEY,
    model_name="qwen-plus",  # Can be changed to other Qwen models
).bind_tools(tools)
```

### Adding Custom Tools

To add new tools, follow this pattern:

```python
@tool
def your_custom_tool(parameter: str) -> str:
    """
    Description of what your tool does
    """
    # Your tool logic here
    return "Tool result"

# Add to tools list
tools.append(your_custom_tool)
tool_map[your_custom_tool.name] = your_custom_tool
```

## Graph Structure

The agent uses LangGraph's StateGraph with the following structure:

```python
builder = StateGraph(GraphState)
builder.add_node("llm", run_llm)
builder.add_node("call_tool", call_tool)
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", check_tool_use_needed, {
    "call_tool": "call_tool",
    "end": END
})
builder.add_edge("call_tool", "llm")
```

## State Management

The `GraphState` class manages:
- **messages**: Conversation history with automatic message aggregation
- **tool_outputs**: List of tool execution results

```python
class GraphState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]
    tool_outputs: List[str] = Field(default_factory=list)
```

## Error Handling

The agent includes basic error handling:
- Tool validation before execution
- Proper error messages for unknown tools
- State consistency maintenance

## Extending the Agent

### Adding New Nodes
```python
def your_custom_node(state: GraphState) -> dict:
    # Your custom logic
    return {"messages": [new_message]}

builder.add_node("custom_node", your_custom_node)
```

### Modifying Conditional Logic
```python
def your_custom_router(state: GraphState) -> str:
    # Your routing logic
    return "next_node_name"

builder.add_conditional_edges("source_node", your_custom_router, {
    "option1": "node1",
    "option2": "node2"
})
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `ALI_API_KEY` environment variable is set
2. **Tool Not Found**: Check tool registration in `tool_map`
3. **State Issues**: Verify `GraphState` model compatibility

### Debug Mode

Enable debug output by checking the printed tool execution messages:
```python
print(f"正在执行工具: {tool_name}")  # Tool execution logging
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Add new tools or features
3. Ensure proper error handling
4. Update documentation
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Alibaba's Qwen](https://help.aliyun.com/zh/dashscope/)
- Uses [LangChain](https://github.com/langchain-ai/langchain) ecosystem 