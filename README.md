# CashFlow Copilot

An explainable AI cash-flow copilot for small businesses.

CashFlow Copilot helps small-business owners understand upcoming cash pressure, identify invoices that may be paid late, prioritize collections work, and model simple revenue, expense, and payment-delay scenarios.

## What it does

- Upload bank transactions and invoice CSVs
- Forecast cash position over 30, 60, or 90 days
- Run revenue and expense what-if scenarios
- Simulate customer payment delays
- Score invoice payment risk with explainable factors
- Estimate expected payment dates
- Prioritize collections actions
- Draft editable payment reminders
- Export forecasts as CSV
- Generate an optional AI management briefing
- Run with a deterministic fallback when no AI API key is configured
- Validate input data and surface financial-safety disclaimers

## Product approach

The MVP deliberately separates financial computation from generative AI.

**Deterministic code handles:**

- Cash balances
- Forecast calculations
- Scenario modelling
- Invoice-risk scoring
- Expected payment-date estimation
- Collections prioritization
- Data-quality checks

**The LLM is used for:**

- Explaining financial results
- Producing a management briefing
- Drafting payment-reminder language

This keeps the core financial logic reproducible and reviewable rather than relying on an LLM for arithmetic or financial decisions.

## Demo

The application includes sample business data, so it can be run immediately without connecting a bank account or uploading private financial information.

The demo includes:

- Transaction history
- Paid invoices
- Open invoices
- Overdue invoices
- Future receivables

## Run locally

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
