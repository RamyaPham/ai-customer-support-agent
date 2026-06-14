"""End-to-end tests for the AI Refund Agent.

Tests the full stack: API endpoints, tools, eligibility engine, and data layer.
LLM-dependent tests use a mock to avoid requiring an API key.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import json
import pytest

from fastapi.testclient import TestClient
from app.main import app
from app.db import get_customer, find_orders, get_order_by_id, get_all_customers, _load_data
from app.tools.tools import (
    lookup_customer, list_orders, get_order, get_refund_policy,
    check_eligibility, issue_refund, escalate_to_human,
)
from app.engine.eligibility import check_refund_eligibility
from app.models import Decision, Customer, Order, OrderItem
from app.policy import load_policy

_load_data()
client = TestClient(app)


# ─── API Endpoint Tests ─────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_ok(self):
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


class TestRunsEndpoint:
    def test_runs_returns_list(self):
        res = client.get("/api/runs")
        assert res.status_code == 200
        assert "runs" in res.json()


class TestChatEndpoint:
    def test_chat_rejects_empty_body(self):
        res = client.post("/api/chat", json={})
        assert res.status_code == 422

    def test_chat_accepts_message(self):
        """Mock the agent graph to test API plumbing without LLM."""
        from langchain_core.messages import AIMessage

        mock_state = {
            "messages": [AIMessage(content="I can help with your refund request.")],
            "trace": [],
            "decision": None,
            "run_id": "test-run-1",
        }
        with patch("app.main.agent_graph") as mock_graph:
            mock_graph.invoke.return_value = mock_state
            res = client.post("/api/chat", json={"message": "I want a refund"})
            assert res.status_code == 200
            data = res.json()
            assert "reply" in data
            assert "run_id" in data
            assert "trace" in data


# ─── Data Layer Tests ────────────────────────────────────────────────

class TestDataLayer:
    def test_15_customers_loaded(self):
        customers = get_all_customers()
        assert len(customers) == 15

    def test_lookup_by_email(self):
        c = get_customer("alice.johnson@email.com")
        assert c is not None
        assert c.customer_id == "CUST-001"

    def test_lookup_by_id(self):
        c = get_customer("CUST-005")
        assert c is not None
        assert c.name == "Emma Wilson"

    def test_lookup_by_name(self):
        c = get_customer("Bob Martinez")
        assert c is not None
        assert c.customer_id == "CUST-002"

    def test_lookup_case_insensitive(self):
        c = get_customer("alice.johnson@EMAIL.COM")
        assert c is not None

    def test_lookup_nonexistent(self):
        c = get_customer("nobody@nowhere.com")
        assert c is None

    def test_find_orders(self):
        orders = find_orders("CUST-001")
        assert len(orders) == 2

    def test_get_order_by_id(self):
        o = get_order_by_id("ORD-1001")
        assert o is not None
        assert o.customer_id == "CUST-001"

    def test_get_order_nonexistent(self):
        o = get_order_by_id("ORD-99999")
        assert o is None


# ─── Tool Tests ──────────────────────────────────────────────────────

class TestTools:
    def test_lookup_customer_tool(self):
        result = lookup_customer.invoke({"identifier": "CUST-001"})
        assert result["customer_id"] == "CUST-001"

    def test_lookup_customer_not_found(self):
        result = lookup_customer.invoke({"identifier": "nobody"})
        assert "error" in result

    def test_list_orders_tool(self):
        result = list_orders.invoke({"customer_id": "CUST-001"})
        assert len(result) == 2

    def test_get_order_tool(self):
        result = get_order.invoke({"order_id": "ORD-1001"})
        assert result["order_id"] == "ORD-1001"

    def test_get_order_not_found(self):
        result = get_order.invoke({"order_id": "ORD-FAKE"})
        assert "error" in result

    def test_get_refund_policy_tool(self):
        result = get_refund_policy.invoke({})
        assert "R1" in result
        assert "R6" in result

    def test_check_eligibility_valid(self):
        result = check_eligibility.invoke({"order_id": "ORD-5001", "customer_id": "CUST-005"})
        assert result["decision"] == "APPROVED"

    def test_check_eligibility_final_sale(self):
        result = check_eligibility.invoke({"order_id": "ORD-1002", "customer_id": "CUST-001"})
        assert result["decision"] == "DENIED"
        assert "R1" in result["rule_ids"]

    def test_check_eligibility_already_refunded(self):
        result = check_eligibility.invoke({"order_id": "ORD-4001", "customer_id": "CUST-004"})
        assert result["decision"] == "DENIED"
        assert "R5" in result["rule_ids"]

    def test_check_eligibility_over_500(self):
        result = check_eligibility.invoke({"order_id": "ORD-2001", "customer_id": "CUST-002"})
        assert result["decision"] == "ESCALATED"
        assert "R2" in result["rule_ids"]

    def test_check_eligibility_over_500_karen(self):
        result = check_eligibility.invoke({"order_id": "ORD-11001", "customer_id": "CUST-011"})
        assert result["decision"] == "ESCALATED"
        assert "R2" in result["rule_ids"]

    def test_check_eligibility_damaged_final_sale(self):
        result = check_eligibility.invoke({"order_id": "ORD-6001", "customer_id": "CUST-006"})
        assert result["decision"] == "APPROVED"

    def test_check_eligibility_wrong_customer(self):
        result = check_eligibility.invoke({"order_id": "ORD-1001", "customer_id": "CUST-002"})
        assert result["decision"] == "DENIED"
        assert "R4" in result["rule_ids"]

    def test_check_eligibility_not_found(self):
        result = check_eligibility.invoke({"order_id": "ORD-FAKE", "customer_id": "CUST-001"})
        assert "error" in result

    def test_issue_refund_valid(self):
        result = issue_refund.invoke({"order_id": "ORD-5001", "customer_id": "CUST-005"})
        assert result["status"] == "REFUNDED"

    def test_issue_refund_rejected_final_sale(self):
        result = issue_refund.invoke({"order_id": "ORD-1002", "customer_id": "CUST-001"})
        assert result["status"] == "REJECTED"

    def test_issue_refund_rejected_already_refunded(self):
        result = issue_refund.invoke({"order_id": "ORD-4001", "customer_id": "CUST-004"})
        assert result["status"] == "REJECTED"

    def test_issue_refund_rejected_wrong_customer(self):
        result = issue_refund.invoke({"order_id": "ORD-1001", "customer_id": "CUST-005"})
        assert result["status"] == "REJECTED"

    def test_escalate_to_human_tool(self):
        result = escalate_to_human.invoke({"order_id": "ORD-2001", "reason": "Over $500"})
        assert result["status"] == "ESCALATED"
        assert result["ticket"] == "ESC-1001"


# ─── Edge Case Scenario Tests ───────────────────────────────────────

class TestEdgeCaseScenarios:
    """Test every edge case scenario from the requirements doc."""

    def test_scenario_happy_path_emma(self):
        """CUST-005 ORD-5001: Valid recent order, should APPROVE."""
        result = check_eligibility.invoke({"order_id": "ORD-5001", "customer_id": "CUST-005"})
        assert result["decision"] == "APPROVED"

    def test_scenario_happy_path_david_usb_hub(self):
        """CUST-004 ORD-4002: Valid recent order, should APPROVE."""
        result = check_eligibility.invoke({"order_id": "ORD-4002", "customer_id": "CUST-004"})
        assert result["decision"] == "APPROVED"

    def test_scenario_final_sale_alice(self):
        """CUST-001 ORD-1002: Final sale phone case, should DENY R1."""
        result = check_eligibility.invoke({"order_id": "ORD-1002", "customer_id": "CUST-001"})
        assert result["decision"] == "DENIED"
        assert "R1" in result["rule_ids"]

    def test_scenario_final_sale_maria(self):
        """CUST-013 ORD-13001: Final sale winter coat, should DENY R1."""
        result = check_eligibility.invoke({"order_id": "ORD-13001", "customer_id": "CUST-013"})
        assert result["decision"] == "DENIED"
        assert "R1" in result["rule_ids"]

    def test_scenario_over_500_bob(self):
        """CUST-002 ORD-2001: $529.98 monitor, should ESCALATE R2."""
        result = check_eligibility.invoke({"order_id": "ORD-2001", "customer_id": "CUST-002"})
        assert result["decision"] == "ESCALATED"
        assert "R2" in result["rule_ids"]

    def test_scenario_over_500_karen(self):
        """CUST-011 ORD-11001: $650 handbag, should ESCALATE R2."""
        result = check_eligibility.invoke({"order_id": "ORD-11001", "customer_id": "CUST-011"})
        assert result["decision"] == "ESCALATED"
        assert "R2" in result["rule_ids"]

    def test_scenario_out_of_window_carol(self):
        """CUST-003 ORD-3001: Delivered March 5, well past 30 days. DENY R3."""
        result = check_eligibility.invoke({"order_id": "ORD-3001", "customer_id": "CUST-003"})
        assert result["decision"] == "DENIED"
        assert "R3" in result["rule_ids"]

    def test_scenario_already_refunded_david(self):
        """CUST-004 ORD-4001: Already refunded speaker. DENY R5."""
        result = check_eligibility.invoke({"order_id": "ORD-4001", "customer_id": "CUST-004"})
        assert result["decision"] == "DENIED"
        assert "R5" in result["rule_ids"]

    def test_scenario_damaged_override_frank(self):
        """CUST-006 ORD-6001: Damaged leather jacket marked final sale. R6 override. APPROVE."""
        result = check_eligibility.invoke({"order_id": "ORD-6001", "customer_id": "CUST-006"})
        assert result["decision"] == "APPROVED"

    def test_scenario_cross_customer_attack(self):
        """CUST-002 tries to refund CUST-001's order. DENY R4."""
        result = check_eligibility.invoke({"order_id": "ORD-1001", "customer_id": "CUST-002"})
        assert result["decision"] == "DENIED"
        assert "R4" in result["rule_ids"]

    def test_scenario_issue_refund_guard_blocks_final_sale(self):
        """issue_refund re-validates: final sale blocked even if LLM calls it."""
        result = issue_refund.invoke({"order_id": "ORD-1002", "customer_id": "CUST-001"})
        assert result["status"] == "REJECTED"

    def test_scenario_issue_refund_guard_blocks_over_500(self):
        """issue_refund re-validates: >$500 blocked."""
        result = issue_refund.invoke({"order_id": "ORD-2001", "customer_id": "CUST-002"})
        assert result["status"] == "REJECTED"

    def test_scenario_issue_refund_allows_valid(self):
        """issue_refund allows valid refund through."""
        result = issue_refund.invoke({"order_id": "ORD-14001", "customer_id": "CUST-014"})
        assert result["status"] == "REFUNDED"
        assert result["amount"] == 39.99


# ─── Policy Document Tests ──────────────────────────────────────────

class TestPolicyDocument:
    def test_policy_contains_all_rules(self):
        policy = load_policy()
        for rule in ["R1", "R2", "R3", "R4", "R5", "R6"]:
            assert rule in policy, f"Policy missing rule {rule}"

    def test_policy_mentions_30_days(self):
        policy = load_policy()
        assert "30 days" in policy

    def test_policy_mentions_500(self):
        policy = load_policy()
        assert "$500" in policy

    def test_policy_mentions_final_sale(self):
        policy = load_policy()
        assert "final sale" in policy.lower()

    def test_policy_mentions_damaged(self):
        policy = load_policy()
        assert "damaged" in policy.lower()


# ─── Tracing Tests ──────────────────────────────────────────────────

class TestTracing:
    def test_trace_endpoint_returns_empty_for_unknown(self):
        res = client.get("/api/runs/nonexistent-run/trace")
        assert res.status_code == 200
        assert res.json()["trace"] == []

    def test_chat_returns_trace_in_response(self):
        from langchain_core.messages import AIMessage
        from app.models import TraceStep
        from app.trace.tracer import TRACE_STORE

        mock_trace = TraceStep(step=0, type="llm", name="agent_call", latency_ms=100, tokens_in=50, tokens_out=30)

        def fake_invoke(state):
            TRACE_STORE["trace-test-run"].append(mock_trace)
            return {
                "messages": [AIMessage(content="Test response")],
                "trace": [mock_trace],
                "decision": None,
                "run_id": "trace-test-run",
            }

        with patch("app.main.agent_graph") as mock_graph:
            mock_graph.invoke.side_effect = fake_invoke
            res = client.post("/api/chat", json={"message": "test", "run_id": "trace-test-run"})
            data = res.json()
            assert len(data["trace"]) >= 1
            assert data["trace"][0]["type"] == "llm"
            assert data["trace"][0]["latency_ms"] == 100
