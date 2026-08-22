from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RiskThresholds:
    medium: int = 40
    high: int = 70


def _customer_payment_history(invoices: pd.DataFrame) -> pd.DataFrame:
    paid = invoices[
        invoices["status"].eq("paid") & invoices["paid_date"].notna()
    ].copy()
    if paid.empty:
        return pd.DataFrame(columns=["customer", "avg_delay_days", "paid_count"])

    paid["delay_days"] = (paid["paid_date"] - paid["due_date"]).dt.days
    history = (
        paid.groupby("customer", as_index=False)
        .agg(avg_delay_days=("delay_days", "mean"), paid_count=("invoice_id", "count"))
    )
    return history


def score_invoices(
    invoices: pd.DataFrame,
    as_of: date | pd.Timestamp | None = None,
    thresholds: RiskThresholds = RiskThresholds(),
) -> pd.DataFrame:
    """Score unpaid invoices using transparent, deterministic features.

    This is a prioritization heuristic for an MVP, not a credit decision model.
    """
    now = pd.Timestamp(as_of or date.today()).normalize()
    df = invoices.copy()
    history = _customer_payment_history(df)
    df = df.merge(history, on="customer", how="left")
    df["avg_delay_days"] = df["avg_delay_days"].fillna(3.0)
    df["paid_count"] = df["paid_count"].fillna(0).astype(int)

    open_mask = ~df["status"].eq("paid")
    open_df = df.loc[open_mask].copy()
    if open_df.empty:
        return open_df

    open_df["days_to_due"] = (open_df["due_date"] - now).dt.days
    open_df["days_overdue"] = (-open_df["days_to_due"]).clip(lower=0)

    median_amount = max(float(open_df["amount"].median()), 1.0)
    amount_ratio = (open_df["amount"] / median_amount).clip(0, 3)

    overdue_component = np.clip(open_df["days_overdue"] / 45, 0, 1) * 45
    history_component = np.clip(open_df["avg_delay_days"] / 30, 0, 1) * 25
    amount_component = np.clip(amount_ratio / 3, 0, 1) * 15
    due_soon_component = np.where(
        open_df["days_to_due"].between(0, 7), 10,
        np.where(open_df["days_to_due"].between(8, 14), 5, 0),
    )
    sparse_history_component = np.where(open_df["paid_count"] == 0, 5, 0)

    open_df["risk_score"] = np.rint(
        overdue_component
        + history_component
        + amount_component
        + due_soon_component
        + sparse_history_component
    ).clip(0, 100).astype(int)

    open_df["risk_level"] = np.select(
        [
            open_df["risk_score"] >= thresholds.high,
            open_df["risk_score"] >= thresholds.medium,
        ],
        ["High", "Medium"],
        default="Low",
    )

    expected_delay = np.maximum(open_df["avg_delay_days"], 0)
    risk_delay = np.where(open_df["risk_level"].eq("High"), 10, np.where(open_df["risk_level"].eq("Medium"), 5, 0))
    open_df["expected_payment_date"] = open_df["due_date"] + pd.to_timedelta(
        np.rint(expected_delay + risk_delay).astype(int), unit="D"
    )
    open_df.loc[open_df["expected_payment_date"] < now, "expected_payment_date"] = now

    def reason(row: pd.Series) -> str:
        reasons: list[str] = []
        if row["days_overdue"] > 0:
            reasons.append(f"{int(row['days_overdue'])} days overdue")
        elif row["days_to_due"] <= 7:
            reasons.append("due within 7 days")
        if row["avg_delay_days"] >= 7:
            reasons.append(f"customer averages {row['avg_delay_days']:.0f} late days")
        if row["amount"] >= median_amount * 1.5:
            reasons.append("large invoice relative to portfolio")
        if row["paid_count"] == 0:
            reasons.append("limited payment history")
        return "; ".join(reasons) if reasons else "low-risk payment pattern"

    open_df["risk_reason"] = open_df.apply(reason, axis=1)
    return open_df.sort_values(["risk_score", "amount"], ascending=[False, False]).reset_index(drop=True)
