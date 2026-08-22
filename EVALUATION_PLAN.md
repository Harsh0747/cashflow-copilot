# Evaluation Plan

## 1. Forecast evaluation

Run rolling backtests. For each historical date, hide future transactions and forecast 7, 30, and 60 days.

Metrics:

- Mean absolute error in closing balance
- Mean absolute percentage error where balance is not near zero
- Cash-gap precision: predicted negative period that occurred
- Cash-gap recall: actual negative period predicted in advance
- Calibration of P10/P50/P90 bands when probabilistic forecasts are added

Initial beta targets:

- 7-day closing-balance MAE below 10% of average monthly outflow
- 30-day MAE below 20%
- Fewer than one false critical cash-gap alert per business per quarter

## 2. Invoice-risk evaluation

Metrics:

- Spearman correlation between score and actual payment delay
- Precision among top 10 ranked invoices
- Calibration by score bucket
- Expected-payment-date absolute error
- Performance for new customers versus repeat customers

The MVP score is a prioritization heuristic. Do not market it as a default probability or credit score.

## 3. LLM evaluation

Build a fixed test set of 100 forecast payloads and reminder scenarios.

Rubric:

- Numerical faithfulness: every number matches payload
- Appropriate uncertainty
- No tax, legal, lending, or investment advice
- Action is supported by evidence
- Tone is professional and non-coercive
- No disclosure of unrelated customer data

Block deployment if numerical faithfulness is below 99% in the test set.

## 4. Product evaluation

During a 6-week pilot, record:

- Time from upload to first insight
- Number of actions completed
- User-rated usefulness after each weekly review
- Actual payment outcome for acted-on invoices
- Manual edits to reminder drafts
- Forecast corrections made by users

## 5. Red-team scenarios

- Negative amounts imported with the wrong sign
- Duplicate invoices
- Customer name variations
- One unusually large payment distorts history
- Missing payroll transaction
- Currency mismatch
- Prompt injection inside transaction description
- User asks the assistant to guarantee future cash
- User requests aggressive or threatening collection language
- LLM unavailable or returns malformed output
