"""Simulated Shopify-style e-commerce data for the dashboard."""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any


def _date_range(start: date, end: date) -> list[date]:
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days + 1)]


def generate_customers(n: int = 200) -> list[dict[str, Any]]:
    """Return a list of simulated customers with order histories."""
    random.seed(42)
    today = date.today()
    customers: list[dict[str, Any]] = []

    for i in range(1, n + 1):
        first_order_date = today - timedelta(days=random.randint(30, 720))
        num_orders = random.choices(
            [1, 2, 3, 4, 5, 6, 7, 8],
            weights=[40, 25, 15, 8, 5, 3, 2, 2],
        )[0]

        orders = []
        order_date = first_order_date
        for j in range(num_orders):
            amount = round(random.uniform(15.0, 120.0), 2)
            orders.append({"order_number": j + 1, "date": str(order_date), "amount": amount})
            order_date += timedelta(days=random.randint(14, 120))
            if order_date > today:
                break

        customers.append(
            {
                "id": i,
                "email": f"customer{i}@example.com",
                "first_order_date": str(first_order_date),
                "orders": orders,
            }
        )
    return customers


_CUSTOMERS = generate_customers()


def get_summary_metrics() -> dict[str, Any]:
    """Top-level KPI cards."""
    total_customers = len(_CUSTOMERS)
    total_orders = sum(len(c["orders"]) for c in _CUSTOMERS)
    total_revenue = sum(o["amount"] for c in _CUSTOMERS for o in c["orders"])
    avg_order_value = total_revenue / total_orders if total_orders else 0
    avg_orders_per_customer = total_orders / total_customers if total_customers else 0
    estimated_ltv = avg_order_value * avg_orders_per_customer

    repeat_customers = sum(1 for c in _CUSTOMERS if len(c["orders"]) > 1)
    retention_rate = (repeat_customers / total_customers * 100) if total_customers else 0

    return {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "avg_order_value": round(avg_order_value, 2),
        "avg_orders_per_customer": round(avg_orders_per_customer, 2),
        "estimated_ltv": round(estimated_ltv, 2),
        "repeat_customer_rate": round(retention_rate, 1),
    }


def get_orders_over_time() -> list[dict[str, Any]]:
    """Monthly order counts and revenue."""
    from collections import defaultdict

    monthly: dict[str, dict[str, float]] = defaultdict(lambda: {"orders": 0, "revenue": 0.0})
    for c in _CUSTOMERS:
        for o in c["orders"]:
            month_key = o["date"][:7]  # YYYY-MM
            monthly[month_key]["orders"] += 1
            monthly[month_key]["revenue"] += o["amount"]

    result = []
    for month in sorted(monthly.keys()):
        result.append(
            {
                "month": month,
                "orders": monthly[month]["orders"],
                "revenue": round(monthly[month]["revenue"], 2),
            }
        )
    return result


def get_retention_cohorts() -> list[dict[str, Any]]:
    """Simple cohort retention: group customers by first-order month,
    then show what % made a repeat purchase in subsequent months."""
    from collections import defaultdict

    cohorts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in _CUSTOMERS:
        cohort_month = c["first_order_date"][:7]
        cohorts[cohort_month].append(c)

    result = []
    for cohort_month in sorted(cohorts.keys()):
        members = cohorts[cohort_month]
        total = len(members)
        retained_m1 = sum(1 for m in members if len(m["orders"]) >= 2)
        retained_m2 = sum(1 for m in members if len(m["orders"]) >= 3)
        retained_m3 = sum(1 for m in members if len(m["orders"]) >= 4)

        result.append(
            {
                "cohort": cohort_month,
                "customers": total,
                "month_0": 100.0,
                "month_1": round(retained_m1 / total * 100, 1) if total else 0,
                "month_2": round(retained_m2 / total * 100, 1) if total else 0,
                "month_3": round(retained_m3 / total * 100, 1) if total else 0,
            }
        )
    return result


def get_ltv_distribution() -> list[dict[str, Any]]:
    """LTV buckets for histogram."""
    buckets = {"$0-50": 0, "$50-100": 0, "$100-200": 0, "$200-500": 0, "$500+": 0}
    for c in _CUSTOMERS:
        ltv = sum(o["amount"] for o in c["orders"])
        if ltv < 50:
            buckets["$0-50"] += 1
        elif ltv < 100:
            buckets["$50-100"] += 1
        elif ltv < 200:
            buckets["$100-200"] += 1
        elif ltv < 500:
            buckets["$200-500"] += 1
        else:
            buckets["$500+"] += 1

    return [{"bucket": k, "customers": v} for k, v in buckets.items()]
