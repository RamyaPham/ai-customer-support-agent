# Chapter 11: LangChain Tools -- Giving the LLM Hands and Eyes

## Why We Chose This

A large language model on its own can only generate text. It cannot look up a customer record, check a database, or issue a refund. LangChain's **tool** abstraction solves this: you write a normal Python function, add the `@tool` decorator, and the LLM can call it by name. The function's docstring becomes the tool's description, which the LLM reads to decide when and how to use it.

## How It Works In Our Project

Our seven tools live in `backend/app/tools/tools.py`. They fall into three categories.

### Reading Tools (Eyes)

These let the LLM look up information. They never modify data.

```python
@tool
def lookup_customer(identifier: str) -> dict:
    """Find a customer by email, customer ID, or full name."""
    c = get_customer(identifier)
    if not c:
        return {"error": "customer_not_found", "message": f"No customer found for '{identifier}'."}
    return c.model_dump(mode="json")

@tool
def list_orders(customer_id: str) -> list[dict]:
    """List all orders for a given customer ID."""
    orders = find_orders(customer_id)
    return [o.model_dump(mode="json") for o in orders]

@tool
def get_order(order_id: str) -> dict:
    """Fetch a single order by order ID."""
    # ...

@tool
def get_refund_policy() -> str:
    """Return the full refund policy text (source of truth)."""
    return load_policy()
```

### Decision Tool (Rulebook)

This tool connects the LLM to the deterministic eligibility engine. The engine -- not the LLM -- computes the verdict.

```python
@tool
def check_eligibility(order_id: str, customer_id: str) -> dict:
    """Check whether an order is eligible for refund per policy rules."""
    order = get_order_by_id(order_id)
    caller = get_customer(customer_id)
    if not order or not caller:
        return {"error": "order_not_found"}
    return check_refund_eligibility(order, caller).model_dump()
```

### Action Tools (Hands)

These tools change state. They are protected by guard logic.

```python
@tool
def issue_refund(order_id: str, customer_id: str) -> dict:
    """Issue a refund for an order. Re-validates eligibility internally."""
    order = get_order_by_id(order_id)
    caller = get_customer(customer_id)
    if not order or not caller:
        return {"status": "REJECTED", "reason": ["Order or customer not found."]}
    result = check_refund_eligibility(order, caller)
    if result.decision.value != "APPROVED":
        return {"status": "REJECTED", "reasons": result.reasons, "rule_ids": result.rule_ids}
    order.refunded = True
    order.status = "refunded"
    return {"status": "REFUNDED", "order_id": order_id, "amount": order.amount}
```

### Why `issue_refund` Re-validates (Defense in Depth)

Notice that `issue_refund` calls `check_refund_eligibility` again internally, even though the LLM already called `check_eligibility` in a previous step. This is intentional. If an attacker tricks the LLM into calling `issue_refund` without first checking eligibility -- or after manipulating the conversation -- the tool itself will reject the refund. The tool trusts the database, not the LLM.

### The Tool Registry

All seven tools are registered in a single list that gets passed to the LLM:

```python
AGENT_TOOLS = [
    lookup_customer, list_orders, get_order, get_refund_policy,
    check_eligibility, issue_refund, escalate_to_human,
]
```

## Key Takeaways

- **The `@tool` decorator** turns any Python function into an LLM-callable tool.
- **Docstrings matter**: the LLM reads them to decide which tool to call and what arguments to pass.
- **Tools enforce boundaries**: the LLM can ask to call a tool, but the tool decides whether to comply.
- **Defense in depth**: `issue_refund` re-validates because trusting the LLM's prior checks is not enough.
