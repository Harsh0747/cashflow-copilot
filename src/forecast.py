from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


def current_balance(transactions: pd.DataFrame) -> float:
    return float(transactions["amount"].sum())


def _weekday_operating_profile(transactions: pd.DataFrame) -> pd.DataFrame:
    tx = transactions.copy()
    tx["day"] = tx["date"].dt.normalize()
    tx["weekday"] = tx["date"].dt.weekday
    tx["inflow"] = tx["amount"].clip(lower=0)
    tx["outflow"] = -tx["amount"].clip(upper=0)

    daily = tx.groupby(["day", "weekday"], as_index=False).agg(
        inflow=("inflow", "sum"), outflow=("outflow", "sum")
    )
    profile = daily.groupby("weekday", as_index=False).agg(
        inflow=("inflow", "median"), outflow=("outflow", "median")
    )
    full = pd.DataFrame({"weekday": range(7)}).merge(profile, on="weekday", how="left")
    full[["inflow", "outflow"]] = full[["inflow", "outflow"]].fillna(0.0)
    return full


def build_forecast(
    transactions: pd.DataFrame,
    scored_invoices: pd.DataFrame,
    as_of: date | pd.Timestamp | None = None,
    horizon_days: int = 60,
    revenue_change_pct: float = 0.0,
    expense_change_pct: float = 0.0,
    payment_delay_days: int = 0,
) -> pd.DataFrame:
    """Create an explainable cash forecast from operating history and invoices."""
    if transactions.empty:
        raise ValueError("At least one transaction is required")

    now = pd.Timestamp(as_of or transactions["date"].max()).normalize()
    start = now + pd.Timedelta(days=1)
    dates = pd.date_range(start, periods=horizon_days, freq="D")
    forecast = pd.DataFrame({"date": dates})
    forecast["weekday"] = forecast["date"].dt.weekday

    profile = _weekday_operating_profile(transactions)
    forecast = forecast.merge(profile, on="weekday", how="left")
    forecast["baseline_inflow"] = forecast["inflow"] * (1 + revenue_change_pct / 100)
    forecast["baseline_outflow"] = forecast["outflow"] * (1 + expense_change_pct / 100)

    forecast["invoice_receipts"] = 0.0
    if not scored_invoices.empty:
        receipts = scored_invoices.copy()
        receipts["receipt_date"] = pd.to_datetime(receipts["expected_payment_date"]) + pd.to_timedelta(
            payment_delay_days, unit="D"
        )
        receipts["collection_probability"] = receipts["risk_level"].map(
            {"Low": 0.95, "Medium": 0.75, "High": 0.50}
        ).fillna(0.75)
        receipts["expected_receipt"] = receipts["amount"] * receipts["collection_probability"]
        receipt_daily = receipts.groupby("receipt_date", as_index=False)["expected_receipt"].sum()
        receipt_daily = receipt_daily.rename(columns={"receipt_date": "date", "expected_receipt": "invoice_receipts"})
        forecast = forecast.drop(columns=["invoice_receipts"]).merge(receipt_daily, on="date", how="left")
        forecast["invoice_receipts"] = forecast["invoice_receipts"].fillna(0.0)

    forecast["total_inflow"] = forecast["baseline_inflow"] + forecast["invoice_receipts"]
    forecast["total_outflow"] = forecast["baseline_outflow"]
    forecast["net_cash_flow"] = forecast["total_inflow"] - forecast["total_outflow"]
    forecast["projected_balance"] = current_balance(transactions) + forecast["net_cash_flow"].cumsum()
    forecast["is_negative"] = forecast["projected_balance"] < 0

    return forecast[
        [
            "date",
            "baseline_inflow",
            "invoice_receipts",
            "total_inflow",
            "total_outflow",
            "net_cash_flow",
            "projected_balance",
            "is_negative",
        ]
    ]


def forecast_summary(forecast: pd.DataFrame) -> dict[str, object]:
    min_row = forecast.loc[forecast["projected_balance"].idxmin()]
    negative = forecast[forecast["is_negative"]]
    return {
        "ending_balance": float(forecast.iloc[-1]["projected_balance"]),
        "minimum_balance": float(min_row["projected_balance"]),
        "minimum_balance_date": pd.Timestamp(min_row["date"]),
        "first_negative_date": None if negative.empty else pd.Timestamp(negative.iloc[0]["date"]),
        "expected_invoice_receipts": float(forecast["invoice_receipts"].sum()),
    }
