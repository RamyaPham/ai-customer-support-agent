from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class Decision(str, Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATED = "ESCALATED"
    NEEDS_INFO = "NEEDS_INFO"


class OrderItem(BaseModel):
    sku: str
    name: str
    price: float
    final_sale: bool = False
    damaged: bool = False


class Order(BaseModel):
    order_id: str
    customer_id: str
    items: list[OrderItem]
    amount: float
    status: str
    purchase_date: datetime
    delivered_date: Optional[datetime] = None
    refunded: bool = False


class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    loyalty_tier: str = "standard"
    created_at: datetime


class EligibilityResult(BaseModel):
    decision: Decision
    reasons: list[str]
    rule_ids: list[str]


class TraceStep(BaseModel):
    step: int
    type: str
    name: str
    input: Any = None
    output: Any = None
    latency_ms: float = 0
    tokens_in: int = 0
    tokens_out: int = 0
    retries: int = 0
    error: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    decision: Optional[Decision] = None
    trace: list[TraceStep] = Field(default_factory=list)
    run_id: str
