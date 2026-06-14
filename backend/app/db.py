import json
from copy import deepcopy
from pathlib import Path
from typing import Optional

from app.models import Customer, Order

DATA_DIR = Path(__file__).parent.parent / "data" / "seed"

_customers: list[Customer] = []
_orders: list[Order] = []
_loaded = False
_raw_cache: dict | None = None


def _load_data():
    global _customers, _orders, _loaded, _raw_cache
    if _loaded:
        return
    data_file = DATA_DIR / "customers.json"
    _raw_cache = json.loads(data_file.read_text())
    _customers.clear()
    _orders.clear()
    for c in _raw_cache["customers"]:
        customer_data = {k: v for k, v in c.items() if k != "orders"}
        _customers.append(Customer(**customer_data))
        for o in c.get("orders", []):
            _orders.append(Order(**o))
    _loaded = True


def reload_data():
    """Reset all data to seed state. Used by tests."""
    global _loaded
    _loaded = False
    _load_data()


def get_customer(identifier: str) -> Optional[Customer]:
    _load_data()
    identifier_lower = identifier.lower().strip()
    for c in _customers:
        if (c.customer_id.lower() == identifier_lower
                or c.email.lower() == identifier_lower
                or c.name.lower() == identifier_lower):
            return c
    return None


def find_orders(customer_id: str) -> list[Order]:
    _load_data()
    return [o for o in _orders if o.customer_id == customer_id]


def get_order_by_id(order_id: str) -> Optional[Order]:
    _load_data()
    for o in _orders:
        if o.order_id == order_id:
            return o
    return None


def get_all_customers() -> list[Customer]:
    _load_data()
    return list(_customers)
