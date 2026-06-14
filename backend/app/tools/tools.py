from langchain_core.tools import tool
from app.db import get_customer, find_orders, get_order_by_id
from app.engine.eligibility import check_refund_eligibility
from app.policy import load_policy


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
    o = get_order_by_id(order_id)
    if not o:
        return {"error": "order_not_found", "message": f"No order found for '{order_id}'."}
    return o.model_dump(mode="json")


@tool
def get_refund_policy() -> str:
    """Return the full refund policy text (source of truth)."""
    return load_policy()


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


@tool
def escalate_to_human(order_id: str, reason: str) -> dict:
    """Escalate a refund request to a human agent for review."""
    return {"status": "ESCALATED", "order_id": order_id, "reason": reason, "ticket": "ESC-1001"}


AGENT_TOOLS = [
    lookup_customer, list_orders, get_order, get_refund_policy,
    check_eligibility, issue_refund, escalate_to_human,
]
