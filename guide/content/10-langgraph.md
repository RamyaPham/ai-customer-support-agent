# Chapter 10: LangGraph -- State Machines for AI Agents

## Why We Chose This

A refund decision is not a single question-and-answer. The agent must identify the customer, find their order, check policy, compute eligibility, and then act. That is a multi-step workflow with branching and loops. LangGraph lets us define this workflow as an explicit **state machine** -- nodes are steps, edges are transitions, and the state carries the full conversation history. This makes the agent's behavior predictable, debuggable, and observable.

## How It Works In Our Project

The agent graph is defined in `backend/app/agent/graph.py`. It has three nodes and four edges.

### The State

```python
class AgentState(MessagesState):
    trace: Annotated[list, operator.add]
    decision: Optional[str]
    run_id: str
```

`AgentState` extends LangGraph's built-in `MessagesState` (which tracks the LLM conversation). We add three fields: `trace` accumulates observability steps, `decision` stores the final verdict, and `run_id` identifies the session.

### The Nodes

**agent** -- Calls the LLM with the conversation history and available tools. The LLM either responds to the user or requests a tool call.

```python
def agent_node(state: AgentState):
    llm = get_llm().bind_tools(AGENT_TOOLS)
    response = llm.invoke(state["messages"])
    return {"messages": [response], "trace": [box["_step"]]}
```

**tools** -- Executes whatever tool the LLM requested (e.g., `lookup_customer`, `check_eligibility`). Captures inputs, outputs, and latency for the trace.

**extract** -- Scans the conversation for verdict keywords (APPROVED, DENIED, ESCALATED, NEEDS_INFO) and stores the result in `state["decision"]`.

### Building the Graph

```python
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("tools", traced_tools_node)
graph_builder.add_node("extract", extract_decision)

graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent", tools_condition)
graph_builder.add_edge("tools", "extract")
graph_builder.add_edge("extract", "agent")

agent_graph = graph_builder.compile()
```

The flow works like this:

1. **START -> agent**: The LLM reads the conversation and decides what to do.
2. **agent -> tools_condition**: LangGraph's built-in `tools_condition` checks if the LLM emitted a tool call. If yes, route to `tools`. If no, route to END (the agent is done talking).
3. **tools -> extract**: After a tool runs, scan for a decision.
4. **extract -> agent**: Return to the LLM so it can process the tool result and decide the next step.

This loop continues until the LLM responds without requesting a tool call -- meaning it has finished and is ready to reply to the user.

### Why a Loop?

A typical refund request requires 3-5 tool calls: look up the customer, find their orders, check eligibility, and possibly issue the refund. Each tool call is one trip around the loop. The LLM decides when to stop looping by simply responding with text instead of a tool call.

## Key Takeaways

- **LangGraph is a state machine framework** for building multi-step AI agent workflows.
- **Nodes** are functions, **edges** are transitions, and **conditional edges** enable branching.
- **The agent loop** (agent -> tools -> extract -> agent) continues until the LLM stops requesting tools.
- **State accumulates** across iterations -- messages, traces, and decisions all persist through the loop.
