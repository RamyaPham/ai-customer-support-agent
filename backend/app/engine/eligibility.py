from datetime import datetime, timezone, timedelta
from app.models import Order, Customer, EligibilityResult, Decision

REFUND_WINDOW_DAYS = 30
ESCALATION_THRESHOLD = 500.0


def check_refund_eligibility(
    order: Order,
    caller: Customer,
    now: datetime | None = None,
) -> EligibilityResult:
    now = now or datetime.now(timezone.utc)

    if order.customer_id != caller.customer_id:
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=["This order does not belong to the requesting customer."],
            rule_ids=["R4"],
        )

    if order.refunded or order.status == "refunded":
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=["This order has already been refunded."],
            rule_ids=["R5"],
        )

    if order.status != "delivered":
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=[f"Order status is '{order.status}' — only delivered orders are eligible for refund."],
            rule_ids=[],
        )

    final_sale_items = [i for i in order.items if i.final_sale and not i.damaged]
    if final_sale_items:
        return EligibilityResult(
            decision=Decision.DENIED,
            reasons=["Final-sale items are not refundable."],
            rule_ids=["R1"],
        )

    if order.delivered_date:
        age = now - order.delivered_date
        if age > timedelta(days=REFUND_WINDOW_DAYS):
            return EligibilityResult(
                decision=Decision.DENIED,
                reasons=[f"Refund window of {REFUND_WINDOW_DAYS} days has passed."],
                rule_ids=["R3"],
            )

    if order.amount > ESCALATION_THRESHOLD:
        return EligibilityResult(
            decision=Decision.ESCALATED,
            reasons=[f"Refunds over ${ESCALATION_THRESHOLD:.0f} require human approval."],
            rule_ids=["R2"],
        )

    return EligibilityResult(
        decision=Decision.APPROVED,
        reasons=["Order meets all refund policy requirements."],
        rule_ids=[],
    )
