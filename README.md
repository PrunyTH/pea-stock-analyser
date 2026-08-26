# PEA Microcap Ranking

A transparent stock-analysis framework designed to compare PEA / PEA-PME eligible
microcaps, initially focused on autonomous systems, robotics, drones, AI infrastructure
and energy storage.

## Free local dashboard

The project includes a Streamlit dashboard and is designed to run **locally for free**.
No paid Streamlit subscription is required.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then launch the dashboard:

```bash
streamlit run app.py
```

Your browser will open the local interface, normally at:

```text
http://localhost:8501
```

The dashboard currently shows:

- company description,
- recent share-price action when Yahoo Finance data is available,
- market cap,
- revenue and forward revenue growth,
- gross margin,
- P/S and EV/Sales,
- cash/debt position,
- forward EBITDA and EBITDA margin,
- quantitative score,
- autonomy exposure,
- dilution/liquidity score,
- overall thesis score,
- comparison with all reviewed companies.

## Desktop icon

A Windows shortcut icon is included at:

```text
assets/pea_stock_analyser.ico
```

After pulling the latest version, point the desktop shortcut to this file from **Properties > Change Icon**.

## Why this exists

The goal is not to find the company with the lowest share price. It is to identify
small companies where:

- the addressable market can grow substantially,
- revenue and margins have room to expand,
- valuation has not already priced in the entire story,
- balance-sheet and dilution risks remain acceptable,
- the product has a meaningful exposure to automation or autonomy.

Every scoring component is transformed so **higher = better**.

## Current scoring model

### Quantitative score

| Factor | Weight |
|---|---:|
| Forward revenue growth | 25% |
| Gross margin | 15% |
| Net cash / market cap | 15% |
| P/S attractiveness | 15% |
| EV/Sales attractiveness | 15% |
| Forward EBITDA margin | 15% |

### Final thesis score

- Quantitative score: 80%
- Autonomy exposure: 10%
- Dilution / liquidity quality: 10%

The exact normalisation ranges live in `ScoreConfig`, so they are easy to change
and later back-test.

## Command-line usage

```bash
python stock_ranker.py
```

This:

1. loads `data/companies.csv`,
2. calculates valuation and financial metrics,
3. ranks the stocks,
4. appends a dated snapshot to `data/history.csv`.

## Tracking over time

`data/history.csv` is intentionally append-only. Each run can create a snapshot of
the metrics and score at that point in time. This will eventually allow us to compare:

- score changes,
- market-cap changes,
- revenue forecast revisions,
- margin improvements/deterioration,
- thesis changes,
- subsequent share-price performance.

## Planned improvements

- Automated market-price retrieval
- Separate historical fundamentals from forward estimates
- Source URLs and source dates per metric
- Revenue CAGR
- Free cash flow / cash runway scoring
- Share dilution history
- Average daily trading value
- Customer concentration
- Recurring revenue percentage
- Insider ownership
- Order backlog / revenue
- Benchmark performance vs the existing PEA ETF
- Back-testing of alternative scoring weights
- Sector-specific scoring profiles
- Automated monthly snapshots

## Important

The initial company data is a research starting point and should be refreshed from
primary company filings before an investment decision.

This is a research tool, not financial advice.
