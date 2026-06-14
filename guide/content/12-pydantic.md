# Chapter 12: Pydantic -- Data Validation in Python

## Why We Chose This

When you build an API, bad data is your biggest source of bugs. A missing field, a wrong type, or an unexpected value can crash your server or -- worse -- silently produce wrong results. Pydantic solves this by letting you define **data models** as Python classes with type annotations. If incoming data does not match the model, Pydantic raises a clear error before your code ever sees it. FastAPI uses Pydantic natively for request and response validation.

## How It Works In Our Project

Our models live in `backend/app/models.py`. Every piece of data that flows through the system has a Pydantic model.

### Business Domain Models

```python
class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    loyalty_tier: str = "standard"
    created_at: datetime

class Order(BaseModel):
    order_id: str
    customer_id: str
    items: list[OrderItem]
    amount: float
    status: str
    purchase_date: datetime
    delivered_date: Optional[datetime] = None
    refunded: bool = False
```

These models represent our core business data. When seed data is loaded from JSON in `db.py`, Pydantic validates every field. If someone adds a customer without an email or an order with a non-numeric amount, the application fails immediately at startup with a descriptive error -- not silently at runtime.

### The Decision Enum

```python
class Decision(str, Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATED = "ESCALATED"
    NEEDS_INFO = "NEEDS_INFO"
```

By defining `Decision` as an enum, we guarantee that only these four values can appear as a decision. Any typo or invalid value is caught at the model level.

### The Eligibility Result

```python
class EligibilityResult(BaseModel):
    decision: Decision
    reasons: list[str]
    rule_ids: list[str]
```

The deterministic engine returns this model. It includes not just the decision but also human-readable reasons and the specific rule IDs that fired. This makes the system auditable -- you can always explain why a refund was approved or denied.

### Observability and API Response Models

```python
class TraceStep(BaseModel):
    step: int
    type: str          # "llm" or "tool"
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
```

`TraceStep` captures everything that happens during a single agent step. `ChatResponse` is the API response model -- FastAPI serializes it to JSON automatically and validates that every response matches this shape. The frontend TypeScript types in `api.ts` mirror these models exactly.

## Key Takeaways

- **Pydantic models** define the shape and types of your data as Python classes.
- **Validation is automatic**: invalid data raises errors before your logic runs.
- **Enums enforce allowed values**: the `Decision` enum prevents invalid verdicts.
- **Models are documentation**: reading the model definitions tells you exactly what data flows through the system.
- **Shared contracts**: backend Pydantic models and frontend TypeScript interfaces stay in sync to prevent integration bugs.
