"""
Central configuration for FI Daily Brief.
Edit this file to customize tickers, email recipients, and report sections.
"""

# ── Treasury yields (via yfinance) ────────────────────────────────────────────
TREASURY_TICKERS = {
    "2Y":  "^IRX",   # 13-week proxy; replace with "^TYX" variants if preferred
    "5Y":  "^FVX",
    "10Y": "^TNX",
    "30Y": "^TYX",
}

# ── Global sovereign ETFs (price → yield implied by duration, or just % chg) ──
GLOBAL_RATES_TICKERS = {
    "UK 10Y Gilt ETF (IGLT)":    "IGLT.L",
    "Japan 10Y JGB ETF (2621)":  "2621.T",
    "Euro Govt Bond ETF (IEAG)": "IEAG.L",
    "EM Local Currency (EMLC)":  "EMLC",
}

# ── Credit proxies (ETF total return / spread proxies) ────────────────────────
CREDIT_TICKERS = {
    "US IG Corp (LQD)":            "LQD",
    "US HY Corp (HYG)":            "HYG",
    "Bank Loans (BKLN)":           "BKLN",    # Invesco Senior Loan ETF
    "Agency MBS (MBB)":            "MBB",
    "Private Credit proxy (BIZD)": "BIZD",    # VanEck BDC Income ETF; best liquid proxy for private credit
    "EM Sovereign (EMB)":          "EMB",
    "EM Corp (EMHY)":              "EMHY",
    "US TIPS (TIP)":               "TIP",
}

# ── Equity markets ────────────────────────────────────────────────────────────
EQUITY_TICKERS = {
    # US
    "S&P 500":          "^GSPC",
    "Dow Jones":        "^DJI",
    "Nasdaq":           "^IXIC",
    "VIX":              "^VIX",
    # Europe
    "Euro Stoxx 50":    "^STOXX50E",
    "DAX":              "^GDAXI",
    "FTSE 100":         "^FTSE",
    # Asia
    "Nikkei 225":       "^N225",
    "Hang Seng":        "^HSI",
    "Shanghai Comp.":   "000001.SS",
}

# ── Commodities ───────────────────────────────────────────────────────────────
COMMODITY_TICKERS = {
    "Gold":             "GC=F",
    "Silver":           "SI=F",
    "WTI Crude":        "CL=F",
    "Brent Crude":      "BZ=F",
    "Natural Gas":      "NG=F",
    "Copper":           "HG=F",
}

# ── FX & USD context ──────────────────────────────────────────────────────────
MACRO_TICKERS = {
    "DXY (USD Index)":  "DX-Y.NYB",
    "EUR/USD":          "EURUSD=X",
    "USD/JPY":          "JPY=X",
    "GBP/USD":          "GBPUSD=X",
    "USD/CNY":          "CNY=X",
}

# ── News sources to scrape ─────────────────────────────────────────────────────
NEWS_SOURCES = [
    {
        "name": "Reuters Markets",
        "url": "https://www.reuters.com/finance/markets/",
        "headline_selector": "a[data-testid='Heading']",
    },
    {
        "name": "Reuters Economy",
        "url": "https://www.reuters.com/economy/",
        "headline_selector": "a[data-testid='Heading']",
    },
    {
        "name": "FT Markets",
        "url": "https://www.ft.com/markets",
        "headline_selector": "a.js-teaser-heading-link",
    },
    {
        "name": "Bloomberg Economy",
        "url": "https://www.bloomberg.com/economy",
        "headline_selector": "a.story-package-module__story__headline-link",
    },
]

MAX_HEADLINES_PER_SOURCE = 10

# ── Claude model ───────────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-6"

# ── Report date/time ──────────────────────────────────────────────────────────
REPORT_TITLE = "Fixed Income Daily Brief"
