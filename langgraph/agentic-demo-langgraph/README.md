# Agentic AI with LangGraph

A progressive tutorial for learning agentic AI orchestration using [LangGraph](https://github.com/langchain-ai/langgraph) and [Anthropic Claude](https://www.anthropic.com/claude).

Each file builds on the previous one — start at `01` and work your way up.

---

## Demos

### 01 · Simple State Graph
**File:** `01_simple_graph.py` · No API key needed

Introduces the 4 core LangGraph primitives without any LLM calls:

| Concept | What it is |
|---|---|
| **State** | A `TypedDict` that flows through every node — the agent's working memory |
| **Nodes** | Pure functions: receive state, return updated state |
| **Edges** | Connections between nodes (fixed or conditional) |
| **END** | Built-in terminal sentinel that stops execution |

```
[START] → initialize → process → process → process → finalize → [END]
                            ↑_______________|  (loops while step_count < 3)
```

---

### 02 · ReAct Tool Agent
**File:** `02_tool_agent.py` · Requires `ANTHROPIC_API_KEY`

Implements the **ReAct (Reason + Act)** pattern: Claude reasons about a question, decides which tool to call, gets the result, and reasons again until it has a final answer.

**Tools included:**
- `calculator` — safe math evaluation (`sqrt`, `**`, trig, etc.)
- `web_search` — simulated knowledge base search
- `get_time` — current date and time

```
[START] → call_llm → execute_tools → call_llm → ... → [END]
               ↓ (no tool calls)
             [END]
```

---

### 03 · Multi-Agent Orchestration
**File:** `03_multi_agent_orchestration.py` · Requires `ANTHROPIC_API_KEY`

Implements the **Supervisor pattern** — a central agent routes work to specialized sub-agents:

```
              ┌─────────────┐
              │  SUPERVISOR │  ← decides who works next
              └──────┬──────┘
         ┌───────────┼───────────┐
         ▼           ▼           ▼
   [RESEARCHER]  [ANALYST]   [WRITER]
   Gathers facts  Finds       Writes
                 insights     output
         └───────────┼───────────┘
                     ▼
               back to SUPERVISOR → FINISH
```

Each agent has a focused system prompt. The supervisor uses `tool_choice` to force a structured routing decision every turn.

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/AroraAnshul/agentic-demo-langgraph.git
cd agentic-demo-langgraph

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Anthropic API key
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=your_key_here
```

---

## Running the Demos

```bash
# No API key needed — great starting point
python 01_simple_graph.py

# Requires ANTHROPIC_API_KEY
python 02_tool_agent.py
python 03_multi_agent_orchestration.py
```

---

## Key Concepts Across All Demos

| Concept | Where it appears |
|---|---|
| State as shared memory | All demos |
| Conditional routing / loops | `01`, `02`, `03` |
| Tool use (define → call → return results) | `02`, `03` |
| Multiple LLM calls in one workflow | `02`, `03` |
| Structured outputs via `tool_choice` | `03` |
| Iteration safety counter | `03` |

---

## Requirements

- Python 3.9+
- `anthropic >= 0.40`
- `langgraph >= 0.2`
- `langchain-anthropic >= 0.3`
- Anthropic API key (for demos 02 and 03)

