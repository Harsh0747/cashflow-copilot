# CashFlow Copilot MVP

A runnable, explainable AI-fintech prototype for small businesses. It forecasts cash, prioritizes risky invoices, creates an action queue, and drafts payment reminders.

## What is included

- CSV upload for bank transactions and invoices
- 30/60/90-day cash forecast
- What-if controls for revenue, expenses, and payment delays
- Explainable invoice-risk score and expected payment date
- Prioritized collections queue
- Payment-reminder drafts
- Optional OpenAI-generated management briefing
- Sample data, tests, Dockerfile, PRD, metrics, and launch plan

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Optional AI briefing

The core product works without an LLM. To enable the generated management briefing:

```bash
cp .env.example .env
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-5.6"
streamlit run app.py
```

The prototype sends only aggregated forecast metrics to the model—not raw transaction descriptions.

## CSV formats

### Transactions

Required columns:

```text
date,description,amount,category
```

Positive amounts are inflows; negative amounts are outflows. `account` is optional.

### Invoices

Required columns:

```text
invoice_id,customer,issue_date,due_date,amount,status,paid_date
```

Use `paid`, `open`, or `overdue` for status. Leave `paid_date` empty for unpaid invoices.

## Test

```bash
pytest -q
```

## Product boundary

This MVP is an operational planning tool. It does not move money, approve loans, provide tax advice, or make autonomous customer decisions. Forecasts and risk scores should be reviewed by a person.
