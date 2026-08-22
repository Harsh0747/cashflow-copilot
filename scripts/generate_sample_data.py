from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
RNG = np.random.default_rng(42)
AS_OF = pd.Timestamp("2026-07-20")


def generate_transactions() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    dates = pd.date_range(AS_OF - pd.Timedelta(days=119), AS_OF, freq="D")

    for d in dates:
        if d.weekday() < 5:
            if RNG.random() < 0.24:
                rows.append({"date": d.date(), "description": "Client payment", "amount": round(RNG.uniform(18000, 65000), 2), "category": "Sales", "account": "Operating"})
            rows.append({"date": d.date(), "description": "Daily operating costs", "amount": -round(RNG.uniform(1200, 4200), 2), "category": "Operations", "account": "Operating"})

        if d.day == 1:
            rows.append({"date": d.date(), "description": "Office rent", "amount": -45000.0, "category": "Rent", "account": "Operating"})
        if d.day == 5:
            rows.append({"date": d.date(), "description": "Payroll", "amount": -185000.0, "category": "Payroll", "account": "Operating"})
        if d.day == 12:
            rows.append({"date": d.date(), "description": "Software subscriptions", "amount": -18000.0, "category": "Software", "account": "Card"})
        if d.day == 18:
            rows.append({"date": d.date(), "description": "GST reserve", "amount": -30000.0, "category": "Tax reserve", "account": "Operating"})

    opening = {"date": (dates.min() - pd.Timedelta(days=1)).date(), "description": "Opening balance", "amount": 700000.0, "category": "Opening balance", "account": "Operating"}
    return pd.DataFrame([opening] + rows).sort_values("date")


def generate_invoices() -> pd.DataFrame:
    customers = {
        "Northstar Retail": 2,
        "BluePeak Labs": 8,
        "UrbanCart": 18,
        "GreenGrid Energy": -1,
        "Nimbus Media": 5,
    }
    rows: list[dict[str, object]] = []
    invoice_no = 1001

    # Paid history to establish customer behavior.
    for customer, typical_delay in customers.items():
        for months_back in [4, 3, 2]:
            issue = AS_OF - pd.DateOffset(months=months_back) - pd.Timedelta(days=12)
            due = issue + pd.Timedelta(days=30)
            delay = max(-3, int(RNG.normal(typical_delay, 3)))
            paid = due + pd.Timedelta(days=delay)
            rows.append({
                "invoice_id": f"INV-{invoice_no}",
                "customer": customer,
                "issue_date": issue.date(),
                "due_date": due.date(),
                "amount": round(RNG.uniform(55000, 160000), 2),
                "status": "paid",
                "paid_date": paid.date(),
            })
            invoice_no += 1

    open_specs = [
        ("UrbanCart", -45, 185000),
        ("BluePeak Labs", -7, 120000),
        ("Northstar Retail", 4, 90000),
        ("Nimbus Media", 10, 145000),
        ("GreenGrid Energy", 24, 70000),
    ]
    for customer, days_to_due, amount in open_specs:
        due = AS_OF + pd.Timedelta(days=days_to_due)
        issue = due - pd.Timedelta(days=30)
        rows.append({
            "invoice_id": f"INV-{invoice_no}",
            "customer": customer,
            "issue_date": issue.date(),
            "due_date": due.date(),
            "amount": amount,
            "status": "overdue" if days_to_due < 0 else "open",
            "paid_date": "",
        })
        invoice_no += 1

    return pd.DataFrame(rows).sort_values("issue_date")


if __name__ == "__main__":
    generate_transactions().to_csv(DATA / "sample_transactions.csv", index=False)
    generate_invoices().to_csv(DATA / "sample_invoices.csv", index=False)
    print("Sample data generated.")
