# CashFlow Copilot — Product Blueprint

## 1. Product thesis

Small-business owners often know their bank balance but cannot confidently answer what it will be in 30–90 days. Data sits across bank statements, invoices, accounting tools, and informal follow-up processes. CashFlow Copilot turns those records into an explainable forecast and a daily action list.

### One-line positioning

**Know what will happen to your cash, why it will happen, and what to do next.**

## 2. Target customer

### Initial ideal customer profile

- India-first service business or agency
- 5–50 employees
- ₹50 lakh–₹10 crore annual revenue
- 20–300 invoices per month
- Uses spreadsheets, Tally, or Zoho Books
- Owner or finance manager still manages collections manually

### Primary persona

**Finance owner / founder**

Jobs to be done:

1. Tell me whether payroll and major bills are safe.
2. Show which unpaid invoices threaten cash most.
3. Help me decide who to follow up with today.
4. Explain changes without requiring finance expertise.

## 3. Problem statement

Finance teams spend time assembling data but still rely on backward-looking reports. Generic accounting dashboards show balances and aged receivables; they rarely combine likely payment timing, operating patterns, scenarios, and next actions in one workflow.

## 4. MVP promise

After uploading two CSV files, a user gets within minutes:

- Current cash and open receivables
- A 30/60/90-day projected balance
- The first projected cash-gap date
- Ranked invoice risk with evidence
- A collections action queue
- Editable payment-reminder drafts

## 5. Scope

### In v1

- CSV ingestion
- Data validation
- Explainable deterministic forecast
- Invoice-delay heuristic
- Scenario simulation
- Action recommendations
- Draft communications
- Exportable forecast
- Human approval before outreach

### Not in v1

- Autonomous payments or transfers
- Lending or underwriting decisions
- Tax filing or tax advice
- Automated customer messaging
- Bank Account Aggregator integration
- Full accounting general ledger
- Multi-entity consolidation

## 6. Core user flow

1. User selects a sample company or uploads transaction and invoice CSVs.
2. Product validates dates, amounts, duplicates, and missing fields.
3. Dashboard shows cash, receivables, projected balance, and alerts.
4. User changes revenue, expense, or collection-delay assumptions.
5. User opens invoice-risk view and reviews reasons.
6. User selects an invoice and edits a reminder.
7. User exports the forecast or works through the action queue.

## 7. Functional requirements

### Data ingestion

- Accept CSV up to 20 MB per file for the pilot.
- Preserve original uploads for audit only with explicit consent.
- Normalize dates, signs, status values, and categories.
- Reject files missing required columns.

### Forecast

- Support 30, 60, and 90 days.
- Start from current cash derived from transaction history.
- Estimate baseline weekday inflow/outflow from historical medians.
- Add risk-adjusted expected invoice receipts.
- Show projected balance and negative-balance date.
- Allow revenue, expense, and customer-delay scenarios.

### Invoice prioritization

- Calculate risk from overdue days, historical customer delay, invoice size, due-date proximity, and sparse history.
- Display score, level, expected payment date, and plain-language reason.
- Never present the score as a credit score.

### AI layer

- Use an LLM for explanation and drafting, not arithmetic.
- Provide only computed aggregates and approved context to the model.
- Require the model to state uncertainty and avoid legal, tax, lending, or investment advice.
- Fall back to deterministic text when the model is unavailable.

## 8. Non-functional requirements

- Encryption in transit and at rest
- Role-based access for owner, finance manager, and viewer
- Tenant isolation
- Audit log for uploads, forecast changes, and reminder approvals
- No model training on customer financial data without explicit agreement
- Deletion controls and documented retention period
- Forecast calculation reproducible from stored inputs and model version

## 9. Success metrics

### North-star metric

**Weekly cash decisions completed**: forecast reviews, collection actions, or approved scenario decisions taken by an active business.

### Activation

- % of new businesses uploading both files
- % receiving a valid forecast within first session
- Time to first useful insight

### Engagement

- Weekly active businesses
- Forecast views per business
- Scenario runs per business
- Action-queue completion rate

### Outcome

- Hours saved per month
- Reduction in overdue receivables
- Amount collected after recommended action
- Forecast error at 7, 30, and 60 days
- Cash-gap alerts acknowledged before the projected date

### Guardrails

- Incorrect negative-cash alerts
- Reminder drafts materially edited by users
- Customer complaints caused by outreach
- Data-import failure rate
- Risk-score disparity by customer segment where relevant

## 10. Pricing hypothesis

- Free: sample data and one manual forecast
- Starter: ₹1,499/month, one entity, monthly uploads
- Growth: ₹4,999/month, integrations, weekly refresh, team access
- Advisor: multi-client workspace for accountants and fractional CFOs

Do not optimize pricing before validating repeated weekly value.

## 11. Go-to-market

### Beachhead

Accounting firms, fractional CFOs, and finance consultants serving 10–50 SME clients. One partner can introduce many businesses and explain the workflow.

### Pilot offer

- 6-week assisted pilot
- CSV onboarding
- Weekly forecast review
- Manual outcome tracking
- No automatic messaging

### Acquisition experiments

1. Partner with five fractional CFOs.
2. Offer a free “cash-risk scan” from exported statements.
3. Publish templates for Tally and Zoho export mapping.
4. Run founder communities and SME-finance workshops.

## 12. Roadmap

### Weeks 1–2: discovery

- Interview 12 founders and 8 finance operators.
- Collect anonymized examples of forecasting spreadsheets.
- Validate the highest-frequency cash decisions.
- Confirm acceptable upload formats and security objections.

### Weeks 3–6: concierge pilot

- Use the included prototype.
- Manually review forecasts before customer delivery.
- Track forecast error and recommended-action outcomes.
- Improve import mapping and explanations.

### Weeks 7–12: private beta

- Add authentication, database, tenant isolation, and audit logs.
- Add saved scenarios and weekly email summaries.
- Build Zoho Books integration first if pilot demand supports it.
- Create an evaluation dashboard.

### Months 4–6: production MVP

- Add accounting integrations.
- Add configurable recurring expenses and payroll schedules.
- Train a payment-delay model only after sufficient consented data.
- Add advisor workspace and billing.

## 13. Key risks and mitigations

| Risk | Mitigation |
|---|---|
| Forecast is trusted too much | Show assumptions, ranges, and source drivers; keep human review |
| Poor CSV quality | Mapping wizard, validation report, and sample templates |
| LLM invents numbers | Compute all figures outside the model; send only verified aggregates |
| Sensitive data exposure | Minimize data, encrypt, redact descriptions sent to models, retention controls |
| Collections message harms relationship | Draft-only workflow, tone controls, approval log |
| Integration delays | CSV-first launch; integrate only after repeat usage is proven |
| Regulatory scope expands | Remain advisory; avoid payments, credit decisions, and tax filing in v1 |

## 14. Decision log

- **CSV before bank integration:** fastest learning and smallest compliance surface.
- **Heuristic before ML:** transparent and testable with little data.
- **LLM for language, not calculations:** reduces hallucination risk.
- **Collections action before broad financial advice:** concrete workflow and measurable value.
- **India-friendly, not India-locked:** rupee display and compatible schemas, with globally reusable core logic.
