"""
Fetches market data: Treasury yields, credit ETFs, global rates, FX, macro.
Uses yfinance for prices and optionally FRED for spread data.
"""

import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from config import TREASURY_TICKERS, CREDIT_TICKERS, GLOBAL_RATES_TICKERS, MACRO_TICKERS, EQUITY_TICKERS, COMMODITY_TICKERS


def _pct_change(current, previous):
    if previous and previous != 0:
        return (current - previous) / abs(previous) * 100
    return None


def _bps_change(current, previous):
    """For yield-like values: return change in basis points."""
    if previous is not None:
        return round((current - previous) * 100, 1)
    return None


def fetch_ticker_data(tickers: dict, period: str = "5d") -> dict:
    """
    Returns dict of {label: {price, prev_close, change_pct, change_abs}} for each ticker.
    """
    results = {}
    symbols = list(tickers.values())
    labels = list(tickers.keys())

    try:
        data = yf.download(symbols, period=period, progress=False, auto_adjust=True)
        close = data["Close"] if "Close" in data else data

        for label, symbol in zip(labels, symbols):
            try:
                if symbol in close.columns:
                    series = close[symbol].dropna()
                elif len(symbols) == 1:
                    series = close.dropna()
                else:
                    results[label] = {"error": "no data"}
                    continue

                if len(series) < 2:
                    results[label] = {"error": "insufficient history"}
                    continue

                current = round(float(series.iloc[-1]), 4)
                previous = round(float(series.iloc[-2]), 4)
                change_abs = round(current - previous, 4)
                change_pct = round(_pct_change(current, previous), 3) if previous else None

                results[label] = {
                    "current": current,
                    "prev_close": previous,
                    "change_abs": change_abs,
                    "change_pct": change_pct,
                    "date": series.index[-1].strftime("%Y-%m-%d"),
                }
            except Exception as e:
                results[label] = {"error": str(e)}

    except Exception as e:
        for label in labels:
            results[label] = {"error": str(e)}

    return results


def fetch_treasury_yields() -> dict:
    """Returns Treasury yield data with bps changes."""
    raw = fetch_ticker_data(TREASURY_TICKERS)
    # Yields are expressed as percentages; change in bps = change_abs * 100 already handled
    # ^TNX etc. are reported as x.xx (e.g. 4.25 = 4.25%), so bps = change_abs * 10
    for label, vals in raw.items():
        if "change_abs" in vals and vals["change_abs"] is not None:
            vals["change_bps"] = round(vals["change_abs"] * 10, 1)
    return raw


def fetch_credit_data() -> dict:
    return fetch_ticker_data(CREDIT_TICKERS)


def fetch_global_rates() -> dict:
    return fetch_ticker_data(GLOBAL_RATES_TICKERS)


def fetch_macro_data() -> dict:
    return fetch_ticker_data(MACRO_TICKERS)


def fetch_equity_data() -> dict:
    return fetch_ticker_data(EQUITY_TICKERS)


def fetch_commodity_data() -> dict:
    return fetch_ticker_data(COMMODITY_TICKERS)


def fetch_all() -> dict:
    """Fetch all market data in one call."""
    print("Fetching market data...")
    return {
        "treasuries": fetch_treasury_yields(),
        "credit": fetch_credit_data(),
        "global_rates": fetch_global_rates(),
        "equities": fetch_equity_data(),
        "commodities": fetch_commodity_data(),
        "macro": fetch_macro_data(),
    }


def format_market_data_for_prompt(market_data: dict) -> str:
    """Converts raw market data dict into a readable text block for Claude."""
    lines = []

    sections = {
        "US Treasury Yields (level = %, change = bps)": market_data.get("treasuries", {}),
        "Credit ETFs (% price change, proxy for spread direction)": market_data.get("credit", {}),
        "Global Sovereign Rates / ETFs": market_data.get("global_rates", {}),
        "Equity Markets (% change)": market_data.get("equities", {}),
        "Commodities (% change)": market_data.get("commodities", {}),
        "FX / USD (% change)": market_data.get("macro", {}),
    }

    for section_title, data in sections.items():
        lines.append(f"\n{section_title}:")
        for label, vals in data.items():
            if "error" in vals:
                lines.append(f"  {label}: data unavailable ({vals['error']})")
            else:
                current = vals.get("current", "N/A")
                chg_bps = vals.get("change_bps")
                chg_pct = vals.get("change_pct")

                if chg_bps is not None:
                    chg_bps = 0.0 if chg_bps == 0 else chg_bps
                    arrow = "+" if chg_bps >= 0 else ""
                    lines.append(f"  {label}: {current}%  ({arrow}{chg_bps} bps)")
                elif chg_pct is not None:
                    arrow = "+" if chg_pct >= 0 else ""
                    lines.append(f"  {label}: {current}  ({arrow}{chg_pct}%)")
                else:
                    lines.append(f"  {label}: {current}")

    return "\n".join(lines)


if __name__ == "__main__":
    data = fetch_all()
    print(format_market_data_for_prompt(data))
