# Chapter 4: Agent Loops -- From Chatbot to Autonomous Agent

## Chatbot vs. Agent

A **chatbot** takes your message, sends it to an LLM, and returns the response. One turn, done. An **agent** is fundamentally different: it can *reason*, *act*, *observe the result*, and *decide what to do next* -- looping as many times as needed to complete a task.

**Analogy:** A chatbot is like a search engine -- you ask, it answers. An agent is like a coworker who you ask to "handle this refund request." They look up the customer, check the order, consult the policy, make a decision, and either process the refund or explain why they cannot. Multiple steps, one request.

## The Agent Loop: Think, Act, Observe, Repeat

Every agent follows this core cycle:

1. **Think**: The LLM reads the conversation and decides what to do next
2. **Act**: It calls a tool (look up customer, check eligibility, etc.)
3. **Observe**: Your code runs the tool and sends the result back
4. **Repeat**: The LLM reads the tool result and decides whether to call another tool or respond to the user

This loop continues until the LLM decides it has enough information to give a final answer.

## How LangGraph Implements This

LangGraph models this loop as a **state machine** -- a graph where nodes are actions and edges define the flow. Here is the actual graph from our project:

```python
# backend/app/agent/graph.py
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)       # LLM thinks
graph_builder.add_node("tools", traced_tools_node) # Tools execute
graph_builder.add_node("extract", extract_decision)# Extract verdict

graph_builder.add_edge(START, "agent")             # Start with LLM
graph_builder.add_conditional_edges(               # If LLM wants a tool,
    "agent", tools_condition                       # go to tools; else END
)
graph_builder.add_edge("tools", "extract")         # After tools, extract
graph_builder.add_edge("extract", "agent")         # Then back to LLM

agent_graph = graph_builder.compile()
```

The flow looks like this:

```
START --> [agent] --needs tool?--> [tools] --> [extract] --> [agent] --done?--> END
              |                                                                  ^
              +------------------no tools needed---------------------------------+
```

The `tools_condition` function is the key decision point: after the LLM responds, LangGraph checks whether the response contains tool calls. If yes, it routes to the `tools` node. If no, the conversation is complete.

## State: The Agent's Memory

The `AgentState` tracks everything across loop iterations:

```python
class AgentState(MessagesState):
    trace: Annotated[list, operator.add]  # Observability data
    decision: Optional[str]               # APPROVED/DENIED/ESCALATED
    run_id: str                           # Unique conversation ID
```

Each loop iteration appends to the message history and trace list, building a complete record of the agent's reasoning.

## Why This Matters

The agent loop is what transforms a simple LLM into a capable assistant. Understanding this pattern -- think, act, observe, repeat -- is the key to understanding how AI agents work, regardless of which framework you use.

## Key Takeaways

- A chatbot is one-turn; an agent loops until the task is complete.
- The core agent cycle is: Think (LLM reasons), Act (tool executes), Observe (result returns), Repeat.
- LangGraph models this as a state machine with nodes (actions) and edges (flow control).
- Conditional edges let the graph decide dynamically whether to call tools or finish.
- State persists across loop iterations, giving the agent memory within a conversation.
