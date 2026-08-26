"""
PEA Microcap Stock Ranking
==========================

A transparent scoring framework for comparing small/micro-cap stocks,
initially focused on autonomous systems, robotics, drones, AI infrastructure
and energy storage.

Higher score is always better.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Optional
import csv


@dataclass
class Company:
    name: str
    ticker: str
    theme: str
    market_cap_m: float
    revenue_m: float
    revenue_forward_m: Optional[float]
    cash_m: float
    debt_m: float
    gross_margin: float
    ebitda_forward_m: Optional[float]
    autonomy_exposure: float
    dilution_liquidity_quality: float
    pea_eligible: str = ""
    broker_access: str = ""
    note: str = ""
    description: str = ""
    yahoo_ticker: str = ""


@dataclass
class ScoreConfig:
    revenue_growth_weight: float = 0.25
    gross_margin_weight: float = 0.15
    balance_sheet_weight: float = 0.15
    ps_weight: float = 0.15
    ev_sales_weight: float = 0.15
    ebitda_margin_weight: float = 0.15

    quantitative_weight: float = 0.80
    autonomy_weight: float = 0.10
    dilution_liquidity_weight: float = 0.10

    revenue_growth_worst: float = -0.50
    revenue_growth_best: float = 0.50
    gross_margin_worst: float = 0.00
    gross_margin_best: float = 0.70
    net_cash_to_mcap_worst: float = -0.50
    net_cash_to_mcap_best: float = 0.25
    ps_worst: float = 4.00
    ps_best: float = 0.50
    ev_sales_worst: float = 4.00
    ev_sales_best: float = 0.50
    ebitda_margin_worst: float = -0.20
    ebitda_margin_best: float = 0.20


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def higher_is_better(value: float, worst: float, best: float) -> float:
    if best == worst:
        raise ValueError("best and worst must differ")
    return clamp((value - worst) / (best - worst) * 100.0)


def lower_is_better(value: float, worst: float, best: float) -> float:
    if worst == best:
        raise ValueError("worst and best must differ")
    return clamp((worst - value) / (worst - best) * 100.0)


def analyse(company: Company, cfg: ScoreConfig = ScoreConfig()) -> dict:
    if company.market_cap_m <= 0:
        raise ValueError(f"{company.name}: market cap must be positive")
    if company.revenue_m <= 0:
        raise ValueError(f"{company.name}: revenue must be positive")

    net_cash = company.cash_m - company.debt_m
    enterprise_value = company.market_cap_m + company.debt_m - company.cash_m
    ps = company.market_cap_m / company.revenue_m
    ev_sales = enterprise_value / company.revenue_m
    net_cash_to_mcap = net_cash / company.market_cap_m

    revenue_growth = (
        company.revenue_forward_m / company.revenue_m - 1.0
        if company.revenue_forward_m is not None
        else None
    )

    ebitda_margin = (
        company.ebitda_forward_m / company.revenue_forward_m
        if company.ebitda_forward_m is not None
        and company.revenue_forward_m
        and company.revenue_forward_m != 0
        else None
    )

    component_scores = {
        "growth_score": higher_is_better(
            revenue_growth, cfg.revenue_growth_worst, cfg.revenue_growth_best
        ) if revenue_growth is not None else 50.0,
        "gross_margin_score": higher_is_better(
            company.gross_margin, cfg.gross_margin_worst, cfg.gross_margin_best
        ),
        "balance_sheet_score": higher_is_better(
            net_cash_to_mcap,
            cfg.net_cash_to_mcap_worst,
            cfg.net_cash_to_mcap_best,
        ),
        "ps_score": lower_is_better(ps, cfg.ps_worst, cfg.ps_best),
        "ev_sales_score": lower_is_better(
            ev_sales, cfg.ev_sales_worst, cfg.ev_sales_best
        ),
        "ebitda_margin_score": higher_is_better(
            ebitda_margin,
            cfg.ebitda_margin_worst,
            cfg.ebitda_margin_best,
        ) if ebitda_margin is not None else 50.0,
    }

    quant_score = (
        component_scores["growth_score"] * cfg.revenue_growth_weight
        + component_scores["gross_margin_score"] * cfg.gross_margin_weight
        + component_scores["balance_sheet_score"] * cfg.balance_sheet_weight
        + component_scores["ps_score"] * cfg.ps_weight
        + component_scores["ev_sales_score"] * cfg.ev_sales_weight
        + component_scores["ebitda_margin_score"] * cfg.ebitda_margin_weight
    )

    final_score = (
        quant_score * cfg.quantitative_weight
        + company.autonomy_exposure * cfg.autonomy_weight
        + company.dilution_liquidity_quality * cfg.dilution_liquidity_weight
    )

    return {
        **asdict(company),
        "net_cash_m": net_cash,
        "enterprise_value_m": enterprise_value,
        "ps": ps,
        "ev_sales": ev_sales,
        "net_cash_to_market_cap": net_cash_to_mcap,
        "revenue_growth_forward": revenue_growth,
        "ebitda_margin_forward": ebitda_margin,
        **component_scores,
        "quant_score": quant_score,
        "final_score": final_score,
    }


def rank(companies: list[Company], cfg: ScoreConfig = ScoreConfig()) -> list[dict]:
    results = [analyse(company, cfg) for company in companies]
    return sorted(results, key=lambda row: row["final_score"], reverse=True)


def load_companies(path: str | Path) -> list[Company]:
    companies = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            companies.append(
                Company(
                    name=row["name"],
                    ticker=row["ticker"],
                    theme=row["theme"],
                    market_cap_m=float(row["market_cap_m"]),
                    revenue_m=float(row["revenue_m"]),
                    revenue_forward_m=float(row["revenue_forward_m"]) if row["revenue_forward_m"] else None,
                    cash_m=float(row["cash_m"]),
                    debt_m=float(row["debt_m"]),
                    gross_margin=float(row["gross_margin"]),
                    ebitda_forward_m=float(row["ebitda_forward_m"]) if row["ebitda_forward_m"] else None,
                    autonomy_exposure=float(row["autonomy_exposure"]),
                    dilution_liquidity_quality=float(row["dilution_liquidity_quality"]),
                    pea_eligible=row.get("pea_eligible", ""),
                    broker_access=row.get("broker_access", ""),
                    note=row.get("note", ""),
                    description=row.get("description", ""),
                    yahoo_ticker=row.get("yahoo_ticker", ""),
                )
            )
    return companies


def save_snapshot(results: list[dict], path: str | Path, snapshot_date: Optional[str] = None) -> None:
    snapshot_date = snapshot_date or date.today().isoformat()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "snapshot_date",
        "name",
        "ticker",
        "market_cap_m",
        "revenue_m",
        "revenue_forward_m",
        "ps",
        "ev_sales",
        "gross_margin",
        "revenue_growth_forward",
        "ebitda_margin_forward",
        "quant_score",
        "final_score",
    ]

    exists = path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            writer.writeheader()
        for row in results:
            writer.writerow({
                "snapshot_date": snapshot_date,
                **{field: row.get(field, "") for field in fields if field != "snapshot_date"},
            })


def print_ranking(results: list[dict]) -> None:
    print(
        f"{'Rank':<5} {'Company':<18} {'MCap €m':>10} "
        f"{'P/S':>7} {'EV/S':>7} {'Quant':>8} {'Final':>8}"
    )
    print("-" * 72)
    for idx, row in enumerate(results, start=1):
        print(
            f"{idx:<5} {row['name']:<18} {row['market_cap_m']:>10.2f} "
            f"{row['ps']:>7.2f} {row['ev_sales']:>7.2f} "
            f"{row['quant_score']:>8.1f} {row['final_score']:>8.1f}"
        )


if __name__ == "__main__":
    base = Path(__file__).parent
    companies = load_companies(base / "data" / "companies.csv")
    results = rank(companies)
    print_ranking(results)
    save_snapshot(results, base / "data" / "history.csv")
