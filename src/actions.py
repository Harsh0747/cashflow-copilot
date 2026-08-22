from __future__ import annotations

import pandas as pd


def prioritized_actions(scored_invoices: pd.DataFrame, forecast: pd.DataFrame) -> pd.DataFrame:
    actions: list[dict[str, object]] = []

    for _, row in scored_invoices.head(10).iterrows():
        if row["days_overdue"] > 0:
            action = "Send an overdue reminder and request a confirmed payment date"
            urgency = "Today" if row["risk_level"] == "High" else "Within 2 days"
        elif row["days_to_due"] <= 7:
            action = "Send a friendly pre-due reminder"
            urgency = "Within 2 days"
        else:
            action = "Monitor; no customer outreach yet"
            urgency = "This week"

        actions.append(
            {
                "priority": row["risk_score"],
                "urgency": urgency,
                "customer": row["customer"],
                "invoice_id": row["invoice_id"],
                "amount": row["amount"],
                "recommended_action": action,
                "why": row["risk_reason"],
            }
        )

    negative = forecast[forecast["is_negative"]]
    if not negative.empty:
        first = pd.Timestamp(negative.iloc[0]["date"]).date()
        actions.insert(
            0,
            {
                "priority": 100,
                "urgency": "Today",
                "customer": "Internal",
                "invoice_id": "Cash runway",
                "amount": abs(float(negative.iloc[0]["projected_balance"])),
                "recommended_action": "Delay discretionary spend or accelerate collections before the projected cash gap",
                "why": f"Projected balance becomes negative on {first}",
            },
        )

    return pd.DataFrame(actions).sort_values("priority", ascending=False).reset_index(drop=True)


def deterministic_reminder(invoice: pd.Series, business_name: str = "Your company") -> str:
    due_date = pd.Timestamp(invoice["due_date"]).strftime("%d %b %Y")
    amount = f"₹{float(invoice['amount']):,.0f}"
    overdue = int(invoice.get("days_overdue", 0))

    if overdue > 0:
        opening = f"Our records show that invoice {invoice['invoice_id']} for {amount}, due on {due_date}, is still outstanding."
        request = "Could you please confirm the payment status and expected payment date?"
    else:
        opening = f"A quick reminder that invoice {invoice['invoice_id']} for {amount} is due on {due_date}."
        request = "Please let us know if you need any supporting documents to process it."

    return (
        f"Hi {invoice['customer']},\n\n"
        f"{opening} {request}\n\n"
        "Thank you,\n"
        f"{business_name}"
    )
