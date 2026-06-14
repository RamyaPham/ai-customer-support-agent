# Chapter 6: Deterministic Engines -- Why the AI Does NOT Make Decisions

## The Core Principle

Here is the most important architectural decision in this entire project: **the LLM never decides whether a refund is approved or denied.** That decision is made by a Python function with hard-coded business rules. The LLM is the communicator; the code is the judge.

**Analogy:** Think of a courtroom. The LLM is the lawyer -- it gathers evidence, presents the case, and explains the outcome to the customer. But the verdict comes from the law (our code), not from the lawyer's opinion. A persuasive argument does not change the law.

## Deterministic vs. Probabilistic

- **Probabilistic** (the LLM): Given the same input, might produce slightly different outputs. Cannot be guaranteed to follow rules 100% of the time. Susceptible to manipulation.
- **Deterministic** (our eligibility engine): Given the same input, always produces the exact same output. Rules are enforced by code, not by hope. Cannot be talked out of a decision.

## Our Eligibility Engine: Rules R1 Through R6

Here is the actual eligibility checking code:

```python
# backend/app/engine/eligibility.py
REFUND_WINDOW_DAYS = 30
ESCALATION_THRESHOLD = 500.0

def check_refund_eligibility(order, caller, now=None):
    now = now or datetime.now(timezone.utc)

    # R4: Order must belong to the requesting customer
    if order.customer_id != caller.customer_id:
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=["This order does not belong to the requesting customer."],
            rule_ids=["R4"],
        )

    # R5: No double refunds
    if order.refunded or order.status == "refunded":
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=["This order has already been refunded."],
            rule_ids=["R5"],
        )

    # Order must be delivered
    if order.status != "delivered":
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=[f"Order status is '{order.status}' -- only delivered "
                     f"orders are eligible for refund."],
            rule_ids=[],
        )

    # R1: No final-sale items (unless damaged)
    final_sale_items = [i for i in order.items
                        if i.final_sale and not i.damaged]
    if final_sale_items:
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=["Final-sale items are not refundable."],
            rule_ids=["R1"],
        )

    # R3: Must be within 30-day window
    if order.delivered_date:
        age = now - order.delivered_date
        if age > timedelta(days=REFUND_WINDOW_DAYS):
            return EligibilityResult(
                decision=Decision.DENIED,
                reasons=["Refund window of 30 days has passed."],
                rule_ids=["R3"],
            )

    # R2: High-value orders require human approval
    if order.amount > ESCALATION_THRESHOLD:
        return EligibilityResult(
            decision=Decision.ESCALATED,
            reasons=["Refunds over $500 require human approval."],
            rule_ids=["R2"],
        )

    # All checks passed
    return EligibilityResult(
        decision=Decision.APPROVED,
        reasons=["Order meets all refund policy requirements."],
        rule_ids=[],
    )
```

Each rule is a simple `if` statement. No ambiguity, no interpretation, no way for a customer to argue their way past it. The function returns one of four decisions: `APPROVED`, `DENIED`, `ESCALATED`, or `NEEDS_INFO`.

## Double Validation

Notice that the `issue_refund` tool calls `check_refund_eligibility` *again* before processing the refund. Even if somehow the LLM tried to call `issue_refund` without checking eligibility first, the refund would still be validated by deterministic code.

## Why This Matters

This pattern -- "the verdict is code, not LLM" -- is the single most important safety mechanism in any AI application that takes real-world actions. It means a prompt injection, a hallucination, or a clever customer cannot cause financial loss.

## Key Takeaways

- Never let an LLM make decisions with financial, legal, or safety consequences.
- Deterministic code always produces the same output for the same input; LLMs do not.
- Each business rule is a simple `if` statement -- explicit, testable, and auditable.
- Double validation (checking eligibility again at execution time) provides defense in depth.
- The LLM's role is communication; the code's role is judgment. Keep them separate.
