import pandas as pd

from src.risk import score_invoices


def test_overdue_invoice_scores_higher_than_future_invoice():
    invoices = pd.DataFrame(
        [
            {
                "invoice_id": "PAID-1",
                "customer": "Slow Co",
                "issue_date": pd.Timestamp("2026-01-01"),
                "due_date": pd.Timestamp("2026-01-31"),
                "amount": 1000,
                "status": "paid",
                "paid_date": pd.Timestamp("2026-02-20"),
            },
            {
                "invoice_id": "OPEN-1",
                "customer": "Slow Co",
                "issue_date": pd.Timestamp("2026-05-01"),
                "due_date": pd.Timestamp("2026-05-31"),
                "amount": 2000,
                "status": "open",
                "paid_date": pd.NaT,
            },
            {
                "invoice_id": "OPEN-2",
                "customer": "New Co",
                "issue_date": pd.Timestamp("2026-07-01"),
                "due_date": pd.Timestamp("2026-08-15"),
                "amount": 1000,
                "status": "open",
                "paid_date": pd.NaT,
            },
        ]
    )

    scored = score_invoices(invoices, as_of=pd.Timestamp("2026-07-20"))
    scores = scored.set_index("invoice_id")["risk_score"]
    assert scores["OPEN-1"] > scores["OPEN-2"]
