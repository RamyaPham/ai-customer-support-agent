# Chapter 3: Tool Calling -- Giving the LLM Hands

## The Problem: LLMs Cannot Do Anything

An LLM can *talk about* looking up an order, but it cannot actually query a database. It can *describe* how to process a refund, but it cannot execute one. It lives entirely in the world of text. To be useful in a real application, it needs **tools** -- functions it can ask your code to execute on its behalf.

**Analogy:** The LLM is a brilliant advisor sitting in a room with no computer, no phone, and no internet. It can tell you exactly what to do, but someone else has to actually do it. Tool calling is the intercom system that lets the advisor say "please look up order ORD-42 in the database" and get the result read back.

## How Tool Calling Works

1. You describe your available tools to the LLM (name, description, parameters)
2. When the LLM decides it needs information or wants to take an action, it returns a structured "tool call" instead of plain text
3. Your code executes the function and sends the result back to the LLM
4. The LLM uses that result to continue its response

## Our Seven Tools

Here are the actual tools from our project, defined using LangChain's `@tool` decorator:

```python
# backend/app/tools/tools.py
@tool
def lookup_customer(identifier: str) -> dict:
    """Find a customer by email, customer ID, or full name."""
    c = get_customer(identifier)
    if not c:
        return {"error": "customer_not_found",
                "message": f"No customer found for '{identifier}'."}
    return c.model_dump(mode="json")

@tool
def check_eligibility(order_id: str, customer_id: str) -> dict:
    """Check whether an order is eligible for refund per policy rules."""
    order = get_order_by_id(order_id)
    caller = get_customer(customer_id)
    if not order:
        return {"error": "order_not_found"}
    if not caller:
        return {"error": "customer_not_found"}
    return check_refund_eligibility(order, caller).model_dump()
```

The `@tool` decorator does two things: it registers the function so the LLM knows about it, and it uses the docstring and type hints to automatically generate the schema the LLM needs to call it correctly.

Our full toolkit:

| Tool | Purpose |
|------|---------|
| `lookup_customer` | Find a customer by email, ID, or name |
| `list_orders` | List all orders for a customer |
| `get_order` | Fetch details of a single order |
| `get_refund_policy` | Return the full refund policy text |
| `check_eligibility` | Run deterministic refund eligibility rules |
| `issue_refund` | Execute a refund (re-validates internally) |
| `escalate_to_human` | Escalate to a human agent |

## Why This Matters

Tool calling is the bridge between an LLM's language ability and your application's real-world capabilities. Without tools, you have a chatbot. With tools, you have an agent that can look things up, check policies, and take action -- all under your code's control.

## Key Takeaways

- LLMs cannot access databases, APIs, or external systems on their own -- they need tools.
- The `@tool` decorator in LangChain turns a Python function into something the LLM can call.
- Tool descriptions (docstrings) are critical: the LLM reads them to decide *when* and *how* to call each tool.
- Your code always executes the tool -- the LLM only requests the call. You control what actually happens.
- Separating tools into small, focused functions makes the system easier to test, secure, and debug.
