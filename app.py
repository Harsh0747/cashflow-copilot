from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.actions import deterministic_reminder, prioritized_actions
from src.ai import generate_finance_summary
from src.data import load_invoices, load_transactions, sample_paths
from src.forecast import build_forecast, current_balance, forecast_summary
from src.risk import score_invoices

BASE_DIR = Path(__file__).resolve().parent

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

st.set_page_config(page_title="CashFlow Copilot", page_icon="💸", layout="wide")
st.title("💸 CashFlow Copilot")
st.caption("Explainable cash forecasting and invoice follow-up for small businesses")

with st.sidebar:
    st.header("Data")
    use_sample = st.toggle("Use sample business", value=True)
    tx_upload = st.file_uploader("Transactions CSV", type="csv", disabled=use_sample)
    inv_upload = st.file_uploader("Invoices CSV", type="csv", disabled=use_sample)

    st.header("Scenario")
    horizon = st.select_slider("Forecast horizon", options=[30, 60, 90], value=60)
    revenue_change = st.slider("Revenue change", -30, 30, 0, 5, format="%d%%")
    expense_change = st.slider("Expense change", -20, 30, 0, 5, format="%d%%")
    payment_delay = st.slider("Extra customer delay", 0, 30, 0, 1, format="%d days")
    business_name = st.text_input("Business name", value="Acme Services")

try:
    if use_sample:
        tx_path, inv_path = sample_paths(BASE_DIR)
        transactions = load_transactions(tx_path)
        invoices = load_invoices(inv_path)
        default_as_of = transactions["date"].max().date()
    else:
        if tx_upload is None or inv_upload is None:
            st.info("Upload both CSV files, or enable the sample business.")
            st.stop()
        transactions = load_transactions(tx_upload)
        invoices = load_invoices(inv_upload)
        default_as_of = min(pd.Timestamp.today().date(), transactions["date"].max().date())
except ValueError as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    as_of = st.date_input("Analysis date", value=default_as_of)

scored = score_invoices(invoices, as_of=as_of)
forecast = build_forecast(
    transactions,
    scored,
    as_of=as_of,
    horizon_days=horizon,
    revenue_change_pct=revenue_change,
    expense_change_pct=expense_change,
    payment_delay_days=payment_delay,
)
summary = forecast_summary(forecast)
actions = prioritized_actions(scored, forecast)

balance = current_balance(transactions)
open_receivables = float(scored["amount"].sum()) if not scored.empty else 0.0
high_risk_amount = float(scored.loc[scored["risk_level"].eq("High"), "amount"].sum()) if not scored.empty else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Current cash", f"₹{balance:,.0f}")
m2.metric(f"Projected cash in {horizon}d", f"₹{summary['ending_balance']:,.0f}")
m3.metric("Open receivables", f"₹{open_receivables:,.0f}")
m4.metric("High-risk receivables", f"₹{high_risk_amount:,.0f}")

first_negative = summary["first_negative_date"]
if first_negative is not None:
    st.error(f"Cash gap projected on {first_negative.strftime('%d %b %Y')} under this scenario.")
else:
    st.success(f"No negative cash balance is projected over the next {horizon} days.")

payload = {
    "analysis_date": as_of,
    "current_cash": round(balance, 2),
    "ending_balance": round(summary["ending_balance"], 2),
    "minimum_balance": round(summary["minimum_balance"], 2),
    "minimum_balance_date": summary["minimum_balance_date"],
    "first_negative_date": first_negative,
    "open_receivables": round(open_receivables, 2),
    "high_risk_receivables": round(high_risk_amount, 2),
    "scenario": {
        "revenue_change_pct": revenue_change,
        "expense_change_pct": expense_change,
        "extra_payment_delay_days": payment_delay,
    },
}

ai_summary = generate_finance_summary(payload)
if ai_summary:
    st.subheader("AI briefing")
    st.markdown(ai_summary)
else:
    st.subheader("Briefing")
    driver = "collections timing" if open_receivables > 0 else "baseline operations"
    st.markdown(
        f"- **Outlook:** projected ending cash is **₹{summary['ending_balance']:,.0f}**.\n"
        f"- **Key driver:** {driver}; expected invoice receipts total **₹{summary['expected_invoice_receipts']:,.0f}**.\n"
        f"- **Biggest risk:** **₹{high_risk_amount:,.0f}** of receivables is high risk.\n"
        f"- **Next action:** work the highest-priority item in the action queue below."
    )

overview_tab, forecast_tab, invoices_tab, actions_tab, data_tab = st.tabs(
    ["Overview", "Forecast", "Invoice risk", "Actions", "Data quality"]
)

with overview_tab:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Projected cash balance")
        st.line_chart(forecast.set_index("date")["projected_balance"], height=360)
    with c2:
        st.subheader("Risk distribution")
        if scored.empty:
            st.info("No open invoices.")
        else:
            risk_counts = scored.groupby("risk_level")["amount"].sum().reindex(["High", "Medium", "Low"]).fillna(0)
            st.bar_chart(risk_counts, height=300)

with forecast_tab:
    st.subheader("Daily forecast")
    display_forecast = forecast.copy()
    money_cols = ["baseline_inflow", "invoice_receipts", "total_inflow", "total_outflow", "net_cash_flow", "projected_balance"]
    display_forecast[money_cols] = display_forecast[money_cols].round(0)
    st.dataframe(display_forecast, use_container_width=True, hide_index=True)
    st.download_button(
        "Download forecast CSV",
        display_forecast.to_csv(index=False).encode("utf-8"),
        file_name="cashflow_forecast.csv",
        mime="text/csv",
    )

with invoices_tab:
    st.subheader("Open invoice prioritization")
    if scored.empty:
        st.info("No open invoices to score.")
    else:
        show_cols = [
            "invoice_id", "customer", "amount", "due_date", "days_overdue",
            "risk_score", "risk_level", "expected_payment_date", "risk_reason"
        ]
        st.dataframe(scored[show_cols], use_container_width=True, hide_index=True)

        selected_id = st.selectbox("Draft reminder for", scored["invoice_id"].tolist())
        selected = scored.loc[scored["invoice_id"].eq(selected_id)].iloc[0]
        st.text_area("Reminder draft", deterministic_reminder(selected, business_name), height=220)

with actions_tab:
    st.subheader("Recommended action queue")
    st.dataframe(actions, use_container_width=True, hide_index=True)

with data_tab:
    st.subheader("Input checks")
    st.write(f"Transactions loaded: **{len(transactions):,}**")
    st.write(f"Invoices loaded: **{len(invoices):,}**")
    st.write(f"Transaction range: **{transactions['date'].min().date()} → {transactions['date'].max().date()}**")
    st.write(f"Uncategorized transactions: **{transactions['category'].eq('Uncategorized').sum():,}**")
    st.write(f"Duplicate invoice IDs: **{invoices['invoice_id'].duplicated().sum():,}**")

st.divider()
st.caption(
    "Forecasts are estimates for operational planning, not financial, tax, legal, lending, or investment advice. "
    "Keep a human reviewer in the loop before contacting customers or changing payment decisions."
)
