import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone, timedelta
import pytest
from app.models import Order, OrderItem, Customer, Decision
from app.engine.eligibility import check_refund_eligibility

NOW = datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc)

CUSTOMER = Customer(
    customer_id="CUST-001",
    name="Test User",
    email="test@test.com",
    loyalty_tier="standard",
    created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
)

OTHER_CUSTOMER = Customer(
    customer_id="CUST-999",
    name="Other User",
    email="other@test.com",
    loyalty_tier="standard",
    created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
)


def _make_order(**overrides) -> Order:
    defaults = {
        "order_id": "ORD-TEST",
        "customer_id": "CUST-001",
        "items": [OrderItem(sku="SKU-1", name="Widget", price=50.0)],
        "amount": 50.0,
        "status": "delivered",
        "purchase_date": datetime(2026, 5, 20, tzinfo=timezone.utc),
        "delivered_date": datetime(2026, 5, 25, tzinfo=timezone.utc),
        "refunded": False,
    }
    defaults.update(overrides)
    return Order(**defaults)


def test_normal_order_approved():
    order = _make_order()
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.APPROVED


def test_final_sale_denied():
    order = _make_order(
        items=[OrderItem(sku="SKU-1", name="Widget", price=50.0, final_sale=True)]
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R1" in result.rule_ids


def test_over_500_escalated():
    order = _make_order(amount=600.0)
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.ESCALATED
    assert "R2" in result.rule_ids


def test_out_of_window_denied():
    order = _make_order(
        delivered_date=datetime(2026, 4, 1, tzinfo=timezone.utc)
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R3" in result.rule_ids


def test_wrong_owner_denied():
    order = _make_order()
    result = check_refund_eligibility(order, OTHER_CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R4" in result.rule_ids


def test_already_refunded_denied():
    order = _make_order(refunded=True, status="refunded")
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R5" in result.rule_ids


def test_damaged_final_sale_approved():
    order = _make_order(
        items=[OrderItem(sku="SKU-1", name="Widget", price=50.0, final_sale=True, damaged=True)]
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.APPROVED


def test_final_sale_takes_priority_over_escalation():
    order = _make_order(
        amount=600.0,
        items=[OrderItem(sku="SKU-1", name="Widget", price=600.0, final_sale=True)]
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R1" in result.rule_ids


def test_ownership_takes_priority_over_everything():
    order = _make_order(
        amount=600.0,
        items=[OrderItem(sku="SKU-1", name="Widget", price=600.0, final_sale=True)]
    )
    result = check_refund_eligibility(order, OTHER_CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
    assert "R4" in result.rule_ids


def test_damaged_final_sale_over_500_escalated():
    order = _make_order(
        amount=600.0,
        items=[OrderItem(sku="SKU-1", name="Widget", price=600.0, final_sale=True, damaged=True)]
    )
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.ESCALATED
    assert "R2" in result.rule_ids


def test_shipped_order_denied():
    order = _make_order(status="shipped", delivered_date=None)
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED


def test_cancelled_order_denied():
    order = _make_order(status="cancelled", delivered_date=None)
    result = check_refund_eligibility(order, CUSTOMER, now=NOW)
    assert result.decision == Decision.DENIED
