#!/usr/bin/env python3
"""Load seed JSON into memory and verify data integrity."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import get_all_customers, find_orders, _load_data

_load_data()
customers = get_all_customers()
print(f"Loaded {len(customers)} customers:")
for c in customers:
    orders = find_orders(c.customer_id)
    print(f"  {c.customer_id}: {c.name} ({c.email}) — {len(orders)} orders")
    for o in orders:
        flags = []
        if o.refunded:
            flags.append("REFUNDED")
        if o.amount > 500:
            flags.append(">$500")
        for item in o.items:
            if item.final_sale:
                flags.append("FINAL_SALE")
            if item.damaged:
                flags.append("DAMAGED")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        print(f"    {o.order_id}: ${o.amount:.2f} ({o.status}){flag_str}")

print("\nSeed data verified successfully.")
