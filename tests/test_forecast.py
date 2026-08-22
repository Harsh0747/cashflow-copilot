import pandas as pd

from src.forecast import build_forecast


def test_forecast_has_requested_horizon_and_running_balance():
    transactions = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-07-18", "2026-07-19", "2026-07-20"]),
            "description": ["sale", "expense", "sale"],
            "amount": [1000.0, -200.0, 500.0],
            "category": ["Sales", "Operations", "Sales"],
            "account": ["Primary", "Primary", "Primary"],
        }
    )
    invoices = pd.DataFrame(
        {
            "expected_payment_date": pd.to_datetime(["2026-07-22"]),
            "amount": [1000.0],
            "risk_level": ["Low"],
        }
    )

    forecast = build_forecast(transactions, invoices, as_of="2026-07-20", horizon_days=30)
    assert len(forecast) == 30
    assert "projected_balance" in forecast.columns
    assert forecast.iloc[-1]["projected_balance"] == forecast.iloc[0]["projected_balance"] + forecast.iloc[1:]["net_cash_flow"].sum()
