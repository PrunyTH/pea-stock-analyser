# PEA Microcap Ranking

A transparent stock-analysis framework designed to compare PEA / PEA-PME eligible
microcaps, initially focused on autonomous systems, robotics, drones, AI infrastructure
and energy storage.

## Free local dashboard

The project includes a Streamlit dashboard and is designed to run **locally for free**.
No paid Streamlit subscription is required.

The current dashboard shows:

- company description / thesis,
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

### 1. Clone the repository

```bash
git clone https://github.com/PrunyTH/pea-stock-analyser.git
cd pea-stock-analyser
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

The current dependencies are free/open-source:

- Streamlit
- pandas
- yfinance

No paid API key is required.

### 4. Start the dashboard

```bash
streamlit run app.py
```

The interface will open in your browser, normally at:

```text
http://localhost:8501
```

Everything runs locally on your computer. Closing the terminal stops the dashboard.

### Price data

Recent price history is requested through the free `yfinance` Python package. Yahoo Finance data can occasionally be delayed, unavailable or rate-limited. If that happens, the dashboard still loads and displays the stored fundamental analysis and ranking.

The stock-analysis tool therefore does **not** depend on a paid data subscription to function.

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

- Automated market-price retrieval and caching
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
- Benchmark performance versus the existing PEA ETF
- Back-testing of alternative scoring weights
- Sector-specific scoring profiles
- Automated monthly snapshots

## Important

The initial company data is a research starting point and should be refreshed from
primary company filings before an investment decision.

This is a research tool, not financial advice.
