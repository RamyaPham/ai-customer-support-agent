"""Adversarial tests for the eligibility engine.

These test that the deterministic engine rejects invalid refunds regardless
of any hypothetical LLM behavior — the engine is the final guard.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
import pytest
from app.models import Order, OrderItem, Customer, Decision
from app.engine.eligibility import check_refund_eligibility
from app.tools.tools import issue_refund
from app.db import _load_data

NOW = datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc)

CUSTOMER = Customer(
    customer_id="CUST-001",
    name="Alice Johnson",
    email="alice.johnson@email.com",
    loyalty_tier="gold",
    created_at=datetime(2023, 1, 15, tzinfo=timezone.utc),
)


def test_final_sale_cannot_be_overridden_by_claims():
    """Customer claims 'it wasn't really final sale' — engine uses DB data, not claims."""
    order = Order(
        order_id="ORD-ADV-1",
        customer_id="CUST-001",
        items=[OrderItem(sku="SKU-1", name="Widget", price=50.0, final_sale=True)],
        amount=50.0,
        status="delivered",
        purchase_date=datetime(2026, 5, 20, tzinfo=timezone.utc),
        delivered_date=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R1" in result.rule_ids


def test_high_value_always_escalated():
    """Even if customer demands immediate approval for >$500."""
    order = Order(
        order_id="ORD-ADV-2",
        customer_id="CUST-001",
        items=[OrderItem(sku="SKU-1", name="Laptop", price=999.99)],
        amount=999.99,
        status="delivered",
        purchase_date=datetime(2026, 5, 20, tzinfo=timezone.utc),
        delivered_date=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.ESCALATED


def test_expired_window_no_exceptions():
    """Customer pleads 'I was in hospital' — window is window."""
    order = Order(
        order_id="ORD-ADV-3",
        customer_id="CUST-001",
        items=[OrderItem(sku="SKU-1", name="Old Item", price=50.0)],
        amount=50.0,
        status="delivered",
        purchase_date=datetime(2026, 3, 1, tzinfo=timezone.utc),
        delivered_date=datetime(2026, 3, 5, tzinfo=timezone.utc),
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R3" in result.rule_ids


def test_double_refund_blocked():
    """Customer tries to refund same order twice."""
    order = Order(
        order_id="ORD-ADV-4",
        customer_id="CUST-001",
        items=[OrderItem(sku="SKU-1", name="Widget", price=50.0)],
        amount=50.0,
        status="refunded",
        purchase_date=datetime(2026, 5, 20, tzinfo=timezone.utc),
        delivered_date=datetime(2026, 5, 25, tzinfo=timezone.utc),
        refunded=True,
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R5" in result.rule_ids


def test_cross_customer_access_blocked():
    """Customer tries to refund another customer's order."""
    other = Customer(
        customer_id="CUST-999",
        name="Evil User",
        email="evil@test.com",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    order = Order(
        order_id="ORD-ADV-5",
        customer_id="CUST-001",
        items=[OrderItem(sku="SKU-1", name="Widget", price=50.0)],
        amount=50.0,
        status="delivered",
        purchase_date=datetime(2026, 5, 20, tzinfo=timezone.utc),
        delivered_date=datetime(2026, 5, 25, tzinfo=timezone.utc),
    )
    result = check_refund_eligibility(order, other, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R4" in result.rule_ids


def test_issue_refund_tool_revalidates():
    """issue_refund tool re-checks eligibility — can't bypass engine."""
    _load_data()
    result = issue_refund.invoke({"order_id": "ORD-1002", "customer_id": "CUST-001"})
    assert result["status"] == "REJECTED"


def test_issue_refund_tool_approves_valid():
    """issue_refund tool allows valid refund."""
    _load_data()
    result = issue_refund.invoke({"order_id": "ORD-5001", "customer_id": "CUST-005"})
    assert result["status"] == "REFUNDED"
