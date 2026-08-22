# Architecture and Data Design

## Prototype architecture

```text
CSV files
   │
   ▼
Validation and normalization
   │
   ├── Transaction history ──► weekday cash-flow profile
   │
   └── Invoice history ──────► customer delay profile ─► invoice risk score
                                    │
                                    ▼
Current cash + baseline operations + risk-adjusted receipts
                                    │
                                    ▼
                              Daily forecast
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              Dashboard charts               Action queue
                                                    │
                                                    ▼
                                      Deterministic or LLM text
```

## Production target

```text
Web app
  │
API gateway / authentication
  │
Tenant-aware application service
  ├── ingestion workers
  ├── forecast service
  ├── invoice-risk service
  ├── action/recommendation service
  └── notification approval service
  │
PostgreSQL + encrypted object storage + audit log
  │
Accounting integrations / Account Aggregator partner / email provider
```

## Core entities

### Organization

- id
- legal_name
- display_name
- currency
- timezone
- retention_policy

### Account

- id
- organization_id
- source
- external_id
- name
- account_type

### Transaction

- id
- organization_id
- account_id
- occurred_at
- description
- amount
- category
- source_record_id
- import_id

### Customer

- id
- organization_id
- name
- contact details
- payment terms

### Invoice

- id
- organization_id
- customer_id
- external_id
- issue_date
- due_date
- amount
- status
- paid_date

### Forecast run

- id
- organization_id
- as_of_date
- horizon_days
- scenario parameters
- model version
- input snapshot hash
- output series

### Recommended action

- id
- forecast_run_id
- invoice_id
- priority
- reason codes
- status
- approved_by
- completed_at

## Model strategy

### Stage 1: deterministic

- Median weekday inflow/outflow
- Explicit invoice collection probabilities by risk level
- Transparent risk weighting
- Scenario controls

### Stage 2: statistical

Once enough clean history exists:

- Quantile cash forecast to produce P10/P50/P90 ranges
- Customer-level survival model for payment timing
- Backtesting by business type and seasonality
- Calibrated probabilities rather than raw classification scores

### Stage 3: learned recommendations

Only after sufficient outcome data:

- Estimate which reminder timing improves payment without increasing complaints
- Keep treatment policies bounded and human-approved
- Exclude protected or inappropriate attributes

## LLM boundary

The LLM may:

- Summarize verified outputs
- Explain drivers
- Draft communications
- Convert natural-language scenarios into validated parameters

The LLM must not:

- Calculate balances
- Invent transactions
- Make credit decisions
- Trigger transfers
- Send customer communication without approval

## Security checklist

- OAuth/OIDC authentication
- Organization-level authorization checks on every query
- Encryption at rest and in transit
- Secret manager for integration credentials
- Short-lived access tokens
- Data minimization before LLM calls
- Tamper-evident audit trail
- Backup and deletion tests
- Incident response runbook
- Vendor and model-provider data-processing review
