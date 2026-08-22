from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import pandas as pd

TRANSACTION_COLUMNS = {"date", "description", "amount", "category"}
INVOICE_COLUMNS = {
    "invoice_id",
    "customer",
    "issue_date",
    "due_date",
    "amount",
    "status",
    "paid_date",
}


def _read_csv(source: str | Path | BinaryIO) -> pd.DataFrame:
    return pd.read_csv(source)


def load_transactions(source: str | Path | BinaryIO) -> pd.DataFrame:
    df = _read_csv(source)
    missing = TRANSACTION_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Transactions CSV is missing columns: {sorted(missing)}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["description"] = df["description"].fillna("Unknown").astype(str)
    df["category"] = df["category"].fillna("Uncategorized").astype(str)
    if "account" not in df.columns:
        df["account"] = "Primary"

    df = df.dropna(subset=["date", "amount"]).sort_values("date")
    return df.reset_index(drop=True)


def load_invoices(source: str | Path | BinaryIO) -> pd.DataFrame:
    df = _read_csv(source)
    missing = INVOICE_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Invoices CSV is missing columns: {sorted(missing)}")

    df = df.copy()
    for col in ["issue_date", "due_date", "paid_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["status"] = df["status"].fillna("open").astype(str).str.lower().str.strip()
    df["customer"] = df["customer"].fillna("Unknown").astype(str)
    df["invoice_id"] = df["invoice_id"].astype(str)

    df = df.dropna(subset=["issue_date", "due_date", "amount"])
    return df.reset_index(drop=True)


def sample_paths(base_dir: str | Path) -> tuple[Path, Path]:
    base = Path(base_dir)
    return base / "data" / "sample_transactions.csv", base / "data" / "sample_invoices.csv"
